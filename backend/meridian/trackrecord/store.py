"""Append-only call log + derived scorecard.

`calls.jsonl` is the immutable source of truth — lines are only ever appended,
never edited or deleted.  The public scorecard is *derived* from it each time
`derive_scorecard` is called so misses can never be silently dropped.
"""
import json
import pathlib
from datetime import datetime, timezone
from typing import Any

from meridian.datafeed.models import Pick


_CALLS_FILENAME = "calls.jsonl"


def _calls_path(data_dir: str) -> pathlib.Path:
    return pathlib.Path(data_dir) / _CALLS_FILENAME


def append_calls(
    picks: list[Pick],
    data_dir: str,
    now: datetime | None = None,
) -> None:
    """Append one JSON line per pick to ``<data_dir>/calls.jsonl``.

    Each line has the fields required by the §7 track-record contract:
      date, rank, token{name,symbol,address}, score_at_call,
      price_at_call_usd, price_now_usd=None, pct_change=None, status="open".

    The file is NEVER rewritten — only ``"a"`` mode is used.
    """
    if now is None:
        now = datetime.now(timezone.utc)

    date_str = now.strftime("%Y-%m-%d")
    path = _calls_path(data_dir)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("a", encoding="utf-8") as fh:
        for pick in picks:
            record: dict[str, Any] = {
                "date": date_str,
                "rank": pick.rank,
                "token": {
                    "name": pick.candidate.name,
                    "symbol": pick.candidate.symbol,
                    "address": pick.candidate.address,
                },
                "score_at_call": pick.composite_score,
                "price_at_call_usd": pick.candidate.price_usd,
                "price_now_usd": None,
                "pct_change": None,
                "status": "open",
            }
            fh.write(json.dumps(record) + "\n")


def load_calls(data_dir: str) -> list[dict]:
    """Read all records from ``<data_dir>/calls.jsonl``.

    Returns an empty list if the file does not exist.
    """
    path = _calls_path(data_dir)
    if not path.exists():
        return []

    calls: list[dict] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                calls.append(json.loads(line))
    return calls


def derive_scorecard(calls: list[dict]) -> dict:
    """Build the §7 ``track-record.json`` shape from a list of call dicts.

    hit_rate = hits / (hits + misses) — returns None when (hits+misses) == 0
    so the UI can display "N/A" rather than a misleading 0%.
    """
    hits = sum(1 for c in calls if c.get("status") == "hit")
    misses = sum(1 for c in calls if c.get("status") == "miss")
    open_count = sum(1 for c in calls if c.get("status") == "open")
    total = len(calls)
    decided = hits + misses
    hit_rate = (hits / decided) if decided > 0 else None

    return {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_calls": total,
            "hits": hits,
            "misses": misses,
            "open": open_count,
            "hit_rate": hit_rate,
        },
        "calls": calls,
    }
