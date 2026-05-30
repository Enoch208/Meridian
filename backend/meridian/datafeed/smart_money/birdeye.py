"""Birdeye top-traders client: per-token leaderboard with realised PnL."""
from __future__ import annotations

import logging
from typing import Optional

import httpx

from .models import WalletObservation

log = logging.getLogger(__name__)

BIRDEYE_BASE = "https://public-api.birdeye.so"


def fetch_top_traders(
    mint: str,
    *,
    api_key: str,
    limit: int = 10,
    client: Optional[httpx.Client] = None,
) -> list[WalletObservation]:
    """Fetch up to `limit` top traders for `mint` by Birdeye's leaderboard.

    Returns ``[]`` on any failure (logged at WARNING). The api-key is sent in
    a header, not the URL, and never appears in log output.
    """
    c = client or httpx.Client(timeout=30)
    url = f"{BIRDEYE_BASE}/defi/v2/tokens/top_traders"
    params = {"address": mint, "limit": max(1, min(limit, 10))}
    headers = {
        "X-API-KEY": api_key,
        "Accept": "application/json",
        "x-chain": "solana",
    }
    try:
        r = c.get(url, params=params, headers=headers)
        r.raise_for_status()
        body = r.json()
    except httpx.HTTPStatusError as e:
        log.warning(
            "birdeye %s for mint=%s: %s",
            e.response.status_code, mint, _truncate(e.response.text, 200),
        )
        return []
    except Exception as e:
        log.warning("birdeye request failed for mint=%s: %s", mint, e)
        return []
    return parse_top_traders(body, mint=mint)


def parse_top_traders(resp: dict, *, mint: str) -> list[WalletObservation]:
    """Map Birdeye's response into WalletObservation rows.

    Birdeye occasionally varies the wrapper shape across endpoints — we accept
    either ``data.items`` or ``data`` as the trader list.
    """
    if not isinstance(resp, dict):
        return []
    data = resp.get("data")
    items: list = []
    if isinstance(data, dict):
        items = data.get("items") or []
    elif isinstance(data, list):
        items = data
    out: list[WalletObservation] = []
    for i, row in enumerate(items):
        if not isinstance(row, dict):
            continue
        addr = row.get("owner") or row.get("address") or row.get("wallet")
        if not addr:
            continue
        out.append(
            WalletObservation(
                address=addr,
                source="birdeye:top_traders",
                token_mint=mint,
                volume_usd=_to_float(row.get("volume") or row.get("volume_usd")),
                trade_count=_to_int(row.get("trade") or row.get("trade_count")),
                pnl_usd=_to_float(row.get("pnl")),
                rank=i + 1,
            )
        )
    return out


def _to_float(v) -> Optional[float]:
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _to_int(v) -> Optional[int]:
    f = _to_float(v)
    return int(f) if f is not None else None


def _truncate(s: str, n: int) -> str:
    return s if len(s) <= n else s[:n] + "…"
