"""CLI: refresh the smart-money watchlist.

    python -m meridian.datafeed.smart_money.refresh
    python -m meridian.datafeed.smart_money.refresh --curated data/smart_money_curated.json --min-appearances 2

Reads HELIUS_API_KEY and BIRDEYE_API_KEY from the environment. If neither is
set, only the curated source is loaded.
"""
from __future__ import annotations

import argparse
import os
from typing import Optional

import httpx

from meridian.config import get_settings

from . import discover, watchlist


def _winners_from_dexscreener_trending(limit: int = 20) -> list[str]:
    """Best-effort: recent SOL token profiles. Replace later with a real
    "top gainers 7d" source or, even better, our own track-record winners."""
    try:
        r = httpx.get(
            "https://api.dexscreener.com/token-profiles/latest/v1",
            timeout=20,
        )
        profiles = r.json()
        return [
            p["tokenAddress"]
            for p in profiles
            if p.get("chainId") == "solana" and p.get("tokenAddress")
        ][:limit]
    except Exception:
        return []


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="meridian.datafeed.smart_money.refresh")
    ap.add_argument("--curated", default="data/smart_money_curated.json")
    ap.add_argument("--min-appearances", type=int, default=2)
    ap.add_argument("--max-winners", type=int, default=20)
    ap.add_argument(
        "--helius-per-token",
        type=int,
        default=30,
        help="how many earliest buyers to pull per winning mint from Helius",
    )
    ap.add_argument(
        "--birdeye-per-token",
        type=int,
        default=10,
        help="how many top traders to pull per winning mint from Birdeye",
    )
    args = ap.parse_args(argv)

    settings = get_settings()
    helius_key = os.getenv("HELIUS_API_KEY", "").strip()
    birdeye_key = os.getenv("BIRDEYE_API_KEY", "").strip()

    if not helius_key and not birdeye_key:
        print(
            "Note: neither HELIUS_API_KEY nor BIRDEYE_API_KEY is set; "
            "only the curated source will be loaded."
        )

    winners = _winners_from_dexscreener_trending(args.max_winners)
    print(f"Discovering against {len(winners)} candidate winner tokens.")

    wallets = discover.discover_wallets(
        winner_mints=winners,
        helius_key=helius_key or None,
        birdeye_key=birdeye_key or None,
        curated_path=args.curated,
        helius_per_token_limit=args.helius_per_token,
        birdeye_per_token_limit=args.birdeye_per_token,
        min_appearances=args.min_appearances,
    )

    print(f"Identified {len(wallets)} smart-money wallets.")
    for w in wallets[:10]:
        masked = f"{w.address[:6]}…{w.address[-4:]}" if len(w.address) > 12 else w.address
        rank_str = f"  avg_rank={w.avg_entry_rank:.1f}" if w.avg_entry_rank else ""
        print(
            f"  {masked}  score={w.score:5.1f}  winners={w.winners_caught}"
            f"{rank_str}  sources={w.sources}"
        )

    watchlist.save_watchlist(wallets, settings.data_dir)
    store_name = "MongoDB" if settings.mongodb_uri else settings.data_dir
    print(f"Saved watchlist to {store_name}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
