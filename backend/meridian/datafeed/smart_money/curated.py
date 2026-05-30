"""Curated seed list — wallets you trust by hand (named KOLs, known whales).

Format (JSON file at the configured path):

    {
      "wallets": [
        {"address": "<solana-pubkey>", "label": "ansem", "source_url": "https://twitter.com/blknoiz06"},
        ...
      ]
    }

Entries with a placeholder address (starting with "<") are silently skipped so
``smart_money_curated.example.json`` can ship as a template without producing
bogus observations.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

from .models import WalletObservation

log = logging.getLogger(__name__)


def load_curated(path: str) -> list[WalletObservation]:
    p = Path(path)
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        log.warning("curated file %s is not valid JSON: %s", path, e)
        return []
    except OSError as e:
        log.warning("could not read curated file %s: %s", path, e)
        return []
    wallets = data.get("wallets") if isinstance(data, dict) else None
    if not isinstance(wallets, list):
        return []
    out: list[WalletObservation] = []
    for w in wallets:
        if not isinstance(w, dict):
            continue
        addr = (w.get("address") or "").strip()
        if not addr or addr.startswith("<"):
            continue
        out.append(
            WalletObservation(
                address=addr,
                source="curated",
                notes=w.get("label") or w.get("note") or "",
            )
        )
    return out
