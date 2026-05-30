"""File-backed TTL cache for source responses.

Why this exists: each Birdeye Standard CU costs us monthly budget, and Helius
free has a per-minute cap. Re-running discovery within a short window — which
happens whenever a deploy retries or a debug run repeats — should not burn
fresh API calls when the upstream data hasn't materially changed.

Layout:

    <DATA_DIR>/cache/<source>/<mint>.json

Each cache file is a thin wrapper:

    {"fetched_at_epoch": 1717000000.5, "fetched_at": "ISO", "data": [...]}

Where ``data`` is a list of plain dicts (``WalletObservation`` serialized via
``dataclasses.asdict``). Schema-evolving the dataclass safely drops unknown
fields on load (``cached_observations`` only sets known fields)."""
from __future__ import annotations

import json
import logging
import pathlib
import re
from dataclasses import asdict, fields
from datetime import datetime, timezone
from typing import Optional

from .models import WalletObservation

log = logging.getLogger(__name__)

CACHE_DIR = "cache"
DEFAULT_TTL_S = 3600  # 1 hour — long enough to absorb noisy retries, short
                      # enough that a refreshed run still reflects today.

_UNSAFE = re.compile(r"[^A-Za-z0-9_.-]")


def _cache_path(data_dir: str, source: str, key: str) -> pathlib.Path:
    safe_source = _UNSAFE.sub("_", source)[:32]
    safe_key = _UNSAFE.sub("_", key)[:96]
    return pathlib.Path(data_dir) / CACHE_DIR / safe_source / f"{safe_key}.json"


def cached_observations(
    data_dir: str,
    source: str,
    key: str,
    *,
    ttl_s: int = DEFAULT_TTL_S,
) -> Optional[list[WalletObservation]]:
    """Return cached observations if present and fresh; otherwise ``None``."""
    path = _cache_path(data_dir, source, key)
    if not path.exists():
        return None
    try:
        wrapper = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        log.debug("cache read failed (%s): %s", path, e)
        return None
    fetched_at = wrapper.get("fetched_at_epoch")
    if not isinstance(fetched_at, (int, float)):
        return None
    age = datetime.now(timezone.utc).timestamp() - fetched_at
    if age >= ttl_s:
        return None
    rows = wrapper.get("data") or []
    known = {f.name for f in fields(WalletObservation)}
    return [
        WalletObservation(**{k: v for k, v in row.items() if k in known})
        for row in rows
        if isinstance(row, dict)
    ]


def write_observations(
    data_dir: str,
    source: str,
    key: str,
    observations: list[WalletObservation],
) -> None:
    """Persist observations to the cache. Cheap and idempotent."""
    path = _cache_path(data_dir, source, key)
    path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    payload = {
        "fetched_at_epoch": now.timestamp(),
        "fetched_at": now.isoformat(),
        "data": [asdict(o) for o in observations],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
