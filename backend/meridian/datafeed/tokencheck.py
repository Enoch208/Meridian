"""Optional server-side token security / honeypot enrichment.

The endpoint URL and the spoofed Origin are read from env (``TOKEN_CHECK_API_URL``
+ ``TOKEN_CHECK_ORIGIN``) and never hard-coded — so the source is configurable
and not embedded in the repo. This runs **server-side only**; the browser never
sees the upstream. Every failure path returns ``None`` so callers degrade to the
normal scoring flow (the security block is purely additive).
"""
from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

import httpx

# A generic mobile UA — many of these read-only check APIs gate on a browser-ish
# client. Nothing here identifies the upstream.
_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
)


def _num(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _tax(details: dict, field: str) -> float | None:
    """Tax fields come as ``{"number": x, "risk": ...}`` or a bare number."""
    raw = details.get(field)
    if isinstance(raw, dict):
        return _num(raw.get("number"))
    return _num(raw)


def extract(raw: Any) -> dict | None:
    """Pull a compact, display-ready subset from the upstream payload (pure).

    Tolerant of missing/renamed fields — anything absent comes back ``None``.
    """
    if not isinstance(raw, dict):
        return None
    hp = raw.get("honeypotDetails") or {}
    cc = raw.get("codeChecks") or {}
    mc = raw.get("marketChecks") or {}

    is_hp = hp.get("isPairHoneypot")
    out = {
        "overall_score": hp.get("overAllScore"),
        "is_honeypot": (bool(is_hp) if is_hp is not None else None),
        "honeypot_reason": hp.get("honeypotReason"),
        "buy_tax": _tax(hp, "buyTax"),
        "sell_tax": _tax(hp, "sellTax"),
        "transfer_tax": _tax(hp, "transferTax"),
        "code_score": cc.get("codeCheckScore"),
        "market_score": mc.get("marketCheckScore"),
        "liquidity_locked_pct": _num(
            mc.get("lockedLiquidityPercent")
            if mc.get("lockedLiquidityPercent") is not None
            else mc.get("lockedLiquidity")
        ),
    }
    # If literally nothing parsed, treat as no data.
    if all(v is None for v in out.values()):
        return None
    return out


def fetch_security(address: str) -> dict | None:
    """Fetch + extract the security check for a token, or ``None`` if disabled
    or the request fails. Configured entirely via env; safe to call always."""
    from meridian.config import get_settings

    settings = get_settings()
    template = settings.token_check_api_url
    if not template:
        return None

    url = (
        template.replace("{address}", address)
        if "{address}" in template
        else f"{template.rstrip('/')}/{address}"
    )
    origin = settings.token_check_origin or (
        f"{urlparse(url).scheme}://{urlparse(url).netloc}"
    )
    headers = {
        "User-Agent": _UA,
        "Origin": origin,
        "Referer": origin.rstrip("/") + "/",
        "Accept": "application/json",
    }

    try:
        resp = httpx.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        return extract(resp.json())
    except Exception:
        return None
