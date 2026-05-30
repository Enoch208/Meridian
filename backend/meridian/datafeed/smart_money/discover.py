"""Discovery orchestrator + aggregation/scoring.

The *quality* of the watchlist is determined here. The rule is:

  - A wallet **earns its spot** by appearing across multiple recent winning
    tokens (the cross-token signal), or by being curated by hand.
  - A single wallet that bought one token early is NOT smart-money — it's a
    coincidence. We require ``min_appearances`` distinct winning tokens.
  - The score blends *breadth* (how many winners they were early on),
    *depth* (how early — lower average rank is better), and any realised
    PnL the source happens to provide.
"""
from __future__ import annotations

import logging
import time
from collections import defaultdict
from datetime import datetime, timezone
from typing import Callable, Optional

import httpx

from . import birdeye, cache, curated, helius
from .models import SmartMoneyWallet, WalletObservation

log = logging.getLogger(__name__)

# Addresses we always strip from results — system accounts, well-known program
# IDs, common burn sinks, and the wrapped-SOL mint. These should never appear
# as a "buyer" in a real swap, but defending against parser surprises is cheap.
EXCLUDED_ADDRESSES: frozenset[str] = frozenset({
    "11111111111111111111111111111111",                    # System program
    "1nc1nerator11111111111111111111111111111111",         # Solana burn
    "So11111111111111111111111111111111111111112",         # Wrapped SOL mint
    "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",         # SPL Token program
    "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL",        # SPL Associated Token
    "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",        # Raydium AMM v4
    "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4",         # Jupiter v6 program
    "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc",         # Orca Whirlpool
    "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",         # Pump.fun program
})


def discover_wallets(
    *,
    winner_mints: list[str],
    helius_key: Optional[str] = None,
    birdeye_key: Optional[str] = None,
    curated_path: Optional[str] = None,
    helius_per_token_limit: int = 30,
    birdeye_per_token_limit: int = 10,
    min_appearances: int = 2,
    birdeye_throttle_s: float = 1.1,   # Birdeye Standard tier = 1 RPS
    helius_throttle_s: float = 0.15,   # Helius free is generous; mild pace anyway
    cache_dir: Optional[str] = None,
    cache_ttl_s: int = cache.DEFAULT_TTL_S,
    client: Optional[httpx.Client] = None,
) -> list[SmartMoneyWallet]:
    """End-to-end pass: pull observations from configured sources, aggregate, score.

    Throttles between calls so the Birdeye free tier (1 RPS) doesn't 429. If
    ``cache_dir`` is provided, per-(source, mint) responses are cached on
    disk and reused within ``cache_ttl_s`` — so retries within an hour are
    free. Cache hits skip the throttle sleep too.
    """
    owns_client = client is None
    c = client or httpx.Client(timeout=30)
    try:
        observations: list[WalletObservation] = []
        if curated_path:
            observations.extend(curated.load_curated(curated_path))

        for mint in winner_mints:
            if helius_key:
                observations.extend(
                    _cached_or_fetch(
                        source="helius:earliest_buyers",
                        key=mint,
                        cache_dir=cache_dir,
                        cache_ttl_s=cache_ttl_s,
                        fetch=lambda: helius.fetch_earliest_buyers(
                            mint, api_key=helius_key,
                            limit=helius_per_token_limit, client=c,
                        ),
                        throttle_s=helius_throttle_s,
                    )
                )
            if birdeye_key:
                observations.extend(
                    _cached_or_fetch(
                        source="birdeye:top_traders",
                        key=mint,
                        cache_dir=cache_dir,
                        cache_ttl_s=cache_ttl_s,
                        fetch=lambda: birdeye.fetch_top_traders(
                            mint, api_key=birdeye_key,
                            limit=birdeye_per_token_limit, client=c,
                        ),
                        throttle_s=birdeye_throttle_s,
                    )
                )

        log.info(
            "smart-money discovery: %d observations across %d tokens",
            len(observations), len(winner_mints),
        )
        return aggregate(observations, min_appearances=min_appearances)
    finally:
        if owns_client:
            c.close()


def _cached_or_fetch(
    *,
    source: str,
    key: str,
    cache_dir: Optional[str],
    cache_ttl_s: int,
    fetch: Callable[[], list[WalletObservation]],
    throttle_s: float,
) -> list[WalletObservation]:
    """Read-through cache: serve from disk if fresh, else call ``fetch`` and
    write the result. Cache hits skip the upstream throttle entirely."""
    if cache_dir:
        cached = cache.cached_observations(cache_dir, source, key, ttl_s=cache_ttl_s)
        if cached is not None:
            log.debug("cache hit %s/%s (%d rows)", source, key[:10], len(cached))
            return cached
    fresh = fetch()
    if cache_dir and fresh:
        cache.write_observations(cache_dir, source, key, fresh)
    if throttle_s > 0:
        time.sleep(throttle_s)
    return fresh


def aggregate(
    observations: list[WalletObservation],
    *,
    min_appearances: int = 2,
) -> list[SmartMoneyWallet]:
    """Collapse observations into a ranked SmartMoneyWallet list."""
    by_addr: dict[str, list[WalletObservation]] = defaultdict(list)
    for o in observations:
        if not o.address or o.address in EXCLUDED_ADDRESSES:
            continue
        by_addr[o.address].append(o)

    now = datetime.now(timezone.utc).isoformat()
    out: list[SmartMoneyWallet] = []
    for addr, obs in by_addr.items():
        is_curated = any(o.source == "curated" for o in obs)
        unique_tokens = {o.token_mint for o in obs if o.token_mint}
        # Quality gate: keep curated wallets always; otherwise require breadth.
        if not is_curated and len(unique_tokens) < min_appearances:
            continue
        sources = sorted({o.source for o in obs})
        ranks = [o.rank for o in obs if isinstance(o.rank, int)]
        avg_rank = (sum(ranks) / len(ranks)) if ranks else None
        pnl_sum = sum(o.pnl_usd for o in obs if isinstance(o.pnl_usd, (int, float)))
        out.append(
            SmartMoneyWallet(
                address=addr,
                score=_score(obs, is_curated=is_curated),
                label=_pick_label(obs) if is_curated else None,
                first_seen=now,
                last_seen=now,
                sources=sources,
                winners_caught=len(unique_tokens),
                avg_entry_rank=avg_rank,
                cumulative_pnl_usd=pnl_sum or None,
                is_curated=is_curated,
            )
        )
    out.sort(key=lambda w: w.score, reverse=True)
    return out


def _pick_label(obs: list[WalletObservation]) -> Optional[str]:
    for o in obs:
        if o.source == "curated" and o.notes:
            return o.notes
    return None


def _score(obs: list[WalletObservation], *, is_curated: bool) -> float:
    """0-100 composite. Curated wallets start at 70 (you vouched for them);
    discovered wallets earn up to 60 by breadth and gain bonuses from being
    early (low rank) and from realised PnL where the source provides it."""
    unique_tokens = len({o.token_mint for o in obs if o.token_mint})
    base = 70.0 if is_curated else min(60.0, unique_tokens * 15.0)

    ranks = [o.rank for o in obs if isinstance(o.rank, int)]
    if ranks:
        avg_rank = sum(ranks) / len(ranks)
        # rank 1 -> +14.5, rank 30 -> 0
        base += max(0.0, (30.0 - avg_rank)) * 0.5

    pnl = sum(o.pnl_usd for o in obs if isinstance(o.pnl_usd, (int, float)))
    if pnl and pnl > 0:
        base += min(15.0, pnl / 1000.0)  # $30k PnL -> +15

    return round(min(100.0, base), 1)
