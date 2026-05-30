"""Helius enhanced-transactions client: who bought a given mint, in chain order.

We use ``sort-order=asc`` so the first N rows are literally the earliest buyers
of that mint — which, when the mint later turns into a winner, is exactly the
smart-money signal we care about."""
from __future__ import annotations

from typing import Optional

import httpx

from .models import WalletObservation

HELIUS_BASE = "https://api-mainnet.helius-rpc.com"


def fetch_earliest_buyers(
    mint: str,
    *,
    api_key: str,
    limit: int = 30,
    client: Optional[httpx.Client] = None,
) -> list[WalletObservation]:
    """Fetch the first `limit` distinct buyers of `mint` (oldest-first)."""
    c = client or httpx.Client(timeout=30)
    url = f"{HELIUS_BASE}/v0/addresses/{mint}/transactions"
    params = {
        "type": "SWAP",
        "limit": min(max(limit, 1), 100),
        "sort-order": "asc",
        "api-key": api_key,
    }
    try:
        r = c.get(url, params=params)
        r.raise_for_status()
        txns = r.json()
    except Exception:
        return []
    return parse_buyers_from_swaps(txns, mint=mint)[:limit]


def parse_buyers_from_swaps(txns: list[dict], *, mint: str) -> list[WalletObservation]:
    """Pull buyer wallets from a list of Helius enhanced swap transactions.

    Deduplicates by address — a wallet only counts once per (mint, fetch),
    using its earliest observed transaction.
    """
    if not isinstance(txns, list):
        return []
    observations: list[WalletObservation] = []
    seen: set[str] = set()
    rank = 0
    for tx in txns:
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
            # Skip burns / null recipients / system accounts
            if buyer and buyer not in {"", "11111111111111111111111111111111"}:
                return buyer
    return None
