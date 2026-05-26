"""Re-pull current prices for logged calls and compute hit/miss status.

Rules (fixed and documented):
  - pct_change = (price_now - price_at_call) / price_at_call * 100
  - status = "hit"  if pct_change >= 50
  - status = "miss" if pct_change <= -50
  - status = "open" otherwise

`update_all` writes a derived ``track-record.json`` but NEVER mutates
``calls.jsonl`` — the immutable source of truth is left byte-for-byte
identical.
"""
import json
import pathlib
from datetime import datetime, timezone
from typing import Callable, Optional

from meridian.trackrecord.store import load_calls, derive_scorecard


def recompute_status(call: dict, price_now: float) -> dict:
    """Return a *new* dict with updated price_now_usd, pct_change, and status.

    The original dict is not mutated.  score_at_call and price_at_call_usd are
    carried over unchanged.
    """
    result = dict(call)  # shallow copy — preserves all existing fields
    price_at_call = call["price_at_call_usd"]
    pct = (price_now - price_at_call) / price_at_call * 100

    result["price_now_usd"] = price_now
    result["pct_change"] = pct

    if pct >= 50:
        result["status"] = "hit"
    elif pct <= -50:
        result["status"] = "miss"
    else:
        result["status"] = "open"

    return result


def update_all(
    data_dir: str,
    price_lookup: Callable[[str], Optional[float]],
) -> None:
    """Refresh statuses for all calls and write ``<data_dir>/track-record.json``.

    ``price_lookup`` is a callable ``address -> current_price_usd | None``
    injected for testability (the default DexScreener implementation is wired
    in run.py / CLI, not here, so this module stays independently testable).

    The function:
    1. Reads ``calls.jsonl`` (via ``load_calls``) — **never writes to it**.
    2. For each call, attempts to get the current price via ``price_lookup``.
    3. If price is available, recomputes pct_change + status.
    4. Writes the resulting scorecard to ``track-record.json``.
    """
    calls = load_calls(data_dir)

    updated_calls: list[dict] = []
    for call in calls:
        address = call.get("token", {}).get("address", "")
        price_now: Optional[float] = None
        if address:
            try:
                price_now = price_lookup(address)
            except Exception:
                price_now = None

        if price_now is not None:
            updated_call = recompute_status(call, price_now)
        else:
            updated_call = dict(call)  # carry forward unchanged

        updated_calls.append(updated_call)

    scorecard = derive_scorecard(updated_calls)

    out_path = pathlib.Path(data_dir) / "track-record.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(scorecard, fh, indent=2)
