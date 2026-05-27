"""Jupiter token enrichment via the public token-search API.

Fills market data DexScreener can miss — notably bonding-curve / launchpad
tokens (e.g. swarms.world launches) that aren't on a standard LP yet — and adds
the token icon, holder count, and real buy/sell counts. Free, no API key.

Endpoint is env-overridable (``JUPITER_API_URL``) with a working default, so it
needs no configuration. Every failure path returns ``None`` — purely additive.
"""
from __future__ import annotations

import os

import httpx

_DEFAULT_URL = "https://lite-api.jup.ag/tokens/v2/search"


def _num(value: object) -> float | None:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def _int(value: object) -> int | None:
    n = _num(value)
    return int(n) if n is not None else None


def fetch_market(mint: str) -> dict | None:
    """Return enriched market data for a mint, or ``None`` if unavailable."""
    url = os.getenv("JUPITER_API_URL", _DEFAULT_URL)
    try:
        resp = httpx.get(url, params={"query": mint}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return None
    return parse_market(data, mint)


def parse_market(data: object, mint: str) -> dict | None:
    """Pull the fields we use out of a token-search payload (pure, defensive).

    The search endpoint returns a list of token objects; we take the one whose
    ``id`` matches the mint.
    """
    if not isinstance(data, list):
        return None
    entry = next(
        (t for t in data if isinstance(t, dict) and t.get("id") == mint), None
    )
    if entry is None:
        return None

    s1 = entry.get("stats1h") or {}
    s24 = entry.get("stats24h") or {}
    out = {
        "usd_price": _num(entry.get("usdPrice")),
        "liquidity_usd": _num(entry.get("liquidity")),
        "fdv": _num(entry.get("fdv")),
        "market_cap": _num(entry.get("mcap")),
        "price_change_24h": _num(s24.get("priceChange")),
        "launchpad": entry.get("launchpad"),
        "icon": entry.get("icon"),
        "holder_count": _int(entry.get("holderCount")),
        "buys_1h": _int(s1.get("numBuys")),
        "sells_1h": _int(s1.get("numSells")),
    }
    if (
        out["usd_price"] is None
        and out["liquidity_usd"] is None
        and out["icon"] is None
    ):
        return None
    return out
