"""Shortlist + append-only call log, with a derived scorecard.

Two backends, chosen at runtime:
  • **MongoDB** when ``MONGODB_URI`` is set — durable across Render restarts.
  • **Local files** otherwise (``latest_shortlist.json`` + ``calls.jsonl``) —
    the default, and what the test suite uses.

``calls`` is append-only in both backends — records are only ever inserted,
never edited or deleted, so the public scorecard (derived in
``derive_scorecard``) can never silently drop a miss.
"""
import json
import pathlib
from datetime import datetime, timezone
from typing import Any

from meridian.datafeed.models import Pick

_CALLS_FILENAME = "calls.jsonl"
_SHORTLIST_FILENAME = "latest_shortlist.json"

# Cached Mongo client (lazy — pymongo is only imported/connected when a
# MONGODB_URI is configured, so file mode needs no Mongo dependency).
_mongo_client = None


def _mongo_db():
    """Return a MongoDB database handle if ``MONGODB_URI`` is set, else ``None``."""
    from meridian.config import get_settings

    settings = get_settings()
    if not settings.mongodb_uri:
        return None

    global _mongo_client
    if _mongo_client is None:
        from pymongo import MongoClient

        _mongo_client = MongoClient(settings.mongodb_uri)
    return _mongo_client[settings.mongodb_db]


def _calls_path(data_dir: str) -> pathlib.Path:
    return pathlib.Path(data_dir) / _CALLS_FILENAME


def _shortlist_path(data_dir: str) -> pathlib.Path:
    return pathlib.Path(data_dir) / _SHORTLIST_FILENAME


# ---------------------------------------------------------------------------
# Shortlist (the latest ranked picks — a single, overwritten document)
# ---------------------------------------------------------------------------


def save_shortlist(shortlist: dict, data_dir: str) -> None:
    """Persist the latest shortlist (overwrites the previous one)."""
    db = _mongo_db()
    if db is not None:
        db.shortlist.replace_one(
            {"_id": "latest"}, {"_id": "latest", **shortlist}, upsert=True
        )
        return

    path = _shortlist_path(data_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(shortlist, indent=2), encoding="utf-8")


def load_shortlist(data_dir: str) -> dict | None:
    """Return the latest shortlist dict, or ``None`` if none has been saved."""
    db = _mongo_db()
    if db is not None:
        doc = db.shortlist.find_one({"_id": "latest"})
        if not doc:
            return None
        doc.pop("_id", None)
        return doc

    path = _shortlist_path(data_dir)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Call log (append-only)
# ---------------------------------------------------------------------------


def _build_records(picks: list[Pick], now: datetime) -> list[dict[str, Any]]:
    date_str = now.strftime("%Y-%m-%d")
    return [
        {
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
        for pick in picks
    ]


def append_calls(
    picks: list[Pick],
    data_dir: str,
    now: datetime | None = None,
) -> None:
    """Append one record per pick to the call log (never rewrites existing ones).

    Each record carries the §7 track-record fields: date, rank,
    token{name,symbol,address}, score_at_call, price_at_call_usd,
    price_now_usd=None, pct_change=None, status="open".
    """
    if now is None:
        now = datetime.now(timezone.utc)
    records = _build_records(picks, now)
    if not records:
        return

    db = _mongo_db()
    if db is not None:
        db.calls.insert_many([dict(r) for r in records])
        return

    path = _calls_path(data_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record) + "\n")


def load_calls(data_dir: str) -> list[dict]:
    """Read all call records in chronological order. Empty list if none."""
    db = _mongo_db()
    if db is not None:
        return [
            {k: v for k, v in doc.items() if k != "_id"}
            for doc in db.calls.find().sort("_id", 1)
        ]

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
