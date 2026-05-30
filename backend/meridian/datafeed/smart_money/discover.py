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

from collections import defaultdict
from datetime import datetime, timezone
from typing import Optional

import httpx

from . import birdeye, curated, helius
from .models import SmartMoneyWallet, WalletObservation

# Addresses we always strip: DEX program accounts, well-known router PDAs,
# the system burn address. Add to this set as bot patterns surface.
EXCLUDED_ADDRESSES: set[str] = {
    "11111111111111111111111111111111",  # System program / null sink
}


def discover_wallets(
    *,
    winner_mints: list[str],
    helius_key: Optional[str] = None,
    birdeye_key: Optional[str] = None,
    curated_path: Optional[str] = None,
    helius_per_token_limit: int = 30,
    birdeye_per_token_limit: int = 10,
    min_appearances: int = 2,
    client: Optional[httpx.Client] = None,
) -> list[SmartMoneyWallet]:
    """End-to-end pass: pull observations from configured sources, aggregate, score."""
    c = client or httpx.Client(timeout=30)
    observations: list[WalletObservation] = []
    if curated_path:
        observations.extend(curated.load_curated(curated_path))
    for mint in winner_mints:
        if helius_key:
            observations.extend(
                helius.fetch_earliest_buyers(
                    mint, api_key=helius_key, limit=helius_per_token_limit, client=c
                )
            )
        if birdeye_key:
            observations.extend(
                birdeye.fetch_top_traders(
                    mint, api_key=birdeye_key, limit=birdeye_per_token_limit, client=c
                )
            )
    return aggregate(observations, min_appearances=min_appearances)


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
