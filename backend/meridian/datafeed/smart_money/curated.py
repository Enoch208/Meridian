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
from pathlib import Path

from .models import WalletObservation


def load_curated(path: str) -> list[WalletObservation]:
    p = Path(path)
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []
    out: list[WalletObservation] = []
    for w in data.get("wallets", []) or []:
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
