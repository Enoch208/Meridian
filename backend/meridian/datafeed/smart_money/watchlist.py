"""Persist the smart-money watchlist — Mongo if configured, JSON otherwise.

Each refresh **upserts** by address: an existing wallet keeps its
``first_seen`` and gets ``score`` / ``last_seen`` / aggregated stats refreshed.
That way a wallet that has been on the list for weeks shows its real tenure
even after a recompute.
"""
from __future__ import annotations

import json
import pathlib
from dataclasses import asdict, fields
from datetime import datetime, timezone
from typing import Optional

from meridian.config import get_settings

from .models import SmartMoneyWallet

WATCHLIST_FILE = "smart_money_wallets.json"
COLLECTION = "smart_money_wallets"


def save_watchlist(wallets: list[SmartMoneyWallet], data_dir: str) -> None:
    settings = get_settings()
    if settings.mongodb_uri:
        _save_mongo(wallets)
    else:
        _save_file(wallets, data_dir)


def load_watchlist(data_dir: str) -> list[SmartMoneyWallet]:
    settings = get_settings()
    if settings.mongodb_uri:
        return _load_mongo()
    return _load_file(data_dir)


# ── file backend ──────────────────────────────────────────────────────────


def _save_file(wallets: list[SmartMoneyWallet], data_dir: str) -> None:
    path = pathlib.Path(data_dir)
    path.mkdir(parents=True, exist_ok=True)
    file_path = path / WATCHLIST_FILE
    existing = _read_existing_file(file_path)
    now = datetime.now(timezone.utc).isoformat()
    merged = _upsert(wallets, existing, now=now)
    file_path.write_text(
        json.dumps({"updated_at": now, "wallets": merged}, indent=2),
        encoding="utf-8",
    )


def _load_file(data_dir: str) -> list[SmartMoneyWallet]:
    path = pathlib.Path(data_dir) / WATCHLIST_FILE
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    return [_to_wallet(row) for row in data.get("wallets", []) if isinstance(row, dict)]


def _read_existing_file(path: pathlib.Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return {w["address"]: w for w in data.get("wallets", []) if w.get("address")}


def _upsert(
    wallets: list[SmartMoneyWallet],
    existing: dict[str, dict],
    *,
    now: str,
) -> list[dict]:
    """Refresh score/stats; preserve original first_seen for existing rows."""
    merged: list[dict] = []
    for w in wallets:
        row = asdict(w)
        prior = existing.get(w.address)
        row["first_seen"] = (prior or {}).get("first_seen") or w.first_seen or now
        row["last_seen"] = now
        merged.append(row)
    # Sort by score desc to keep the file scannable by hand.
    merged.sort(key=lambda r: r.get("score", 0), reverse=True)
    return merged


# ── mongo backend ─────────────────────────────────────────────────────────


def _save_mongo(wallets: list[SmartMoneyWallet]) -> None:
    from meridian.trackrecord.store import _mongo_db  # reuse cached client

    db = _mongo_db()
    if db is None:
        return
    coll = db[COLLECTION]
    now = datetime.now(timezone.utc).isoformat()
    for w in wallets:
        coll.update_one(
            {"address": w.address},
            {
                "$set": {
                    "score": w.score,
                    "label": w.label,
                    "sources": w.sources,
                    "winners_caught": w.winners_caught,
                    "avg_entry_rank": w.avg_entry_rank,
                    "cumulative_pnl_usd": w.cumulative_pnl_usd,
                    "is_curated": w.is_curated,
                    "notes": w.notes,
                    "last_seen": now,
                },
                "$setOnInsert": {"address": w.address, "first_seen": now},
            },
            upsert=True,
        )


def _load_mongo() -> list[SmartMoneyWallet]:
    from meridian.trackrecord.store import _mongo_db

    db = _mongo_db()
    if db is None:
        return []
    out: list[SmartMoneyWallet] = []
    for row in db[COLLECTION].find().sort("score", -1):
        row.pop("_id", None)
        out.append(_to_wallet(row))
    return out


def _to_wallet(row: dict) -> SmartMoneyWallet:
    """Defensive: drop unknown fields so schema evolution doesn't break load()."""
    known = {f.name for f in fields(SmartMoneyWallet)}
    return SmartMoneyWallet(**{k: v for k, v in row.items() if k in known})
