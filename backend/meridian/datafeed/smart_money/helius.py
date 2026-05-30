"""Helius enhanced-transactions client: who bought a given mint, in chain order.

We use ``sort-order=asc`` so the first N rows are literally the earliest buyers
of that mint — which, when the mint later turns into a winner, is exactly the
smart-money signal we care about.
"""
from __future__ import annotations

import logging
from typing import Optional

import httpx

from .models import WalletObservation

log = logging.getLogger(__name__)

HELIUS_BASE = "https://api-mainnet.helius-rpc.com"

# Addresses that may appear as recipients in token transfers but are never a
# real user buyer (system accounts, common burn sinks).
_SYSTEM_SINKS = frozenset({
    "",
    "11111111111111111111111111111111",                    # System program
    "1nc1nerator11111111111111111111111111111111",         # Solana burn
})


def fetch_earliest_buyers(
    mint: str,
    *,
    api_key: str,
    limit: int = 30,
    client: Optional[httpx.Client] = None,
) -> list[WalletObservation]:
    """Fetch the first `limit` distinct buyers of `mint` (oldest-first).

    Returns ``[]`` on any failure (logged at WARNING). The api-key never appears
    in log output — only the redacted URL.
    """
    c = client or httpx.Client(timeout=30)
    url = f"{HELIUS_BASE}/v0/addresses/{mint}/transactions"
    params = {
        "type": "SWAP",
        "limit": max(1, min(limit, 100)),
        "sort-order": "asc",
        "api-key": api_key,
    }
    try:
        r = c.get(url, params=params)
        r.raise_for_status()
        body = r.json()
    except httpx.HTTPStatusError as e:
        log.warning(
            "helius %s for mint=%s: %s",
            e.response.status_code, mint, _truncate(e.response.text, 200),
        )
        return []
    except Exception as e:  # network, JSON decode, etc.
        log.warning("helius request failed for mint=%s: %s", mint, e)
        return []
    if not isinstance(body, list):
        log.debug("helius returned non-list for mint=%s: %s", mint, _truncate(repr(body), 120))
        return []
    return parse_buyers_from_swaps(body, mint=mint)[:limit]


def parse_buyers_from_swaps(txns: list[dict], *, mint: str) -> list[WalletObservation]:
    """Pull buyer wallets from a list of Helius enhanced swap transactions.

    Defensive: sorts by transaction timestamp ascending before processing, so
    rank corresponds to true earliest appearance even if the API returns
    out-of-order rows. Deduplicates by address — a wallet only counts once per
    fetch, keyed by its earliest swap.
    """
    if not isinstance(txns, list):
        return []
    ordered = sorted(txns, key=lambda t: t.get("timestamp") or 0)
    observations: list[WalletObservation] = []
    seen: set[str] = set()
    rank = 0
    for tx in ordered:
        buyer = _identify_buyer(tx, mint=mint)
        if not buyer or buyer in seen:
            continue
        seen.add(buyer)
        rank += 1
        observations.append(
            WalletObservation(
                address=buyer,
                source="helius:earliest_buyers",
                token_mint=mint,
                buy_timestamp=tx.get("timestamp"),
                rank=rank,
            )
        )
    return observations


def _identify_buyer(tx: dict, *, mint: str) -> Optional[str]:
    """The buyer is the recipient of the target mint in a swap."""
    for tt in tx.get("tokenTransfers") or []:
        if tt.get("mint") == mint:
            buyer = tt.get("toUserAccount")
            if buyer and buyer not in _SYSTEM_SINKS:
                return buyer
    return None


def _truncate(s: str, n: int) -> str:
    return s if len(s) <= n else s[:n] + "…"
