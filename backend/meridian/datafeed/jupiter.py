"""Jupiter price + liquidity lookup.

Fills market data DexScreener can miss — notably bonding-curve / launchpad
tokens (e.g. swarms.world launches) that aren't on a standard LP pool yet.
Free, no API key. The endpoint is env-overridable (``JUPITER_API_URL``) with a
working default, so it needs no configuration. Every failure path returns
``None`` — purely additive.
"""
from __future__ import annotations

import os

import httpx

_DEFAULT_URL = "https://lite-api.jup.ag/price/v3"


def _num(value: object) -> float | None:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def fetch_market(mint: str) -> dict | None:
    """Return ``{usd_price, liquidity_usd, price_change_24h}`` for a mint.

    ``None`` if the token has no Jupiter route or the request fails.
    """
    url = os.getenv("JUPITER_API_URL", _DEFAULT_URL)
    try:
        resp = httpx.get(url, params={"ids": mint}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return None
    return parse_market(data, mint)


def parse_market(data: object, mint: str) -> dict | None:
    """Pull the fields we use out of a price/v3 payload (pure, defensive)."""
    if not isinstance(data, dict):
        return None
    entry = data.get(mint)
    if not isinstance(entry, dict):
        return None
    out = {
        "usd_price": _num(entry.get("usdPrice")),
        "liquidity_usd": _num(entry.get("liquidity")),
        "price_change_24h": _num(entry.get("priceChange24h")),
    }
    if out["usd_price"] is None and out["liquidity_usd"] is None:
        return None
    return out
