"""CLI: refresh the smart-money watchlist.

    python -m meridian.datafeed.smart_money.refresh
    python -m meridian.datafeed.smart_money.refresh --max-winners 15 -v

Reads HELIUS_API_KEY and BIRDEYE_API_KEY from the environment. If neither is
set, only the curated source is loaded.
"""
from __future__ import annotations

import argparse
import logging
import os
from typing import Optional

import httpx

from meridian.config import get_settings

from . import discover, watchlist

log = logging.getLogger(__name__)


def _winners_from_dexscreener_trending(limit: int = 20) -> list[str]:
    """Best-effort: recent SOL token profiles. Replace later with a real
    "top gainers 7d" source or, even better, our own track-record winners."""
    try:
        r = httpx.get(
            "https://api.dexscreener.com/token-profiles/latest/v1",
            timeout=20,
        )
        r.raise_for_status()
        profiles = r.json()
    except Exception as e:
        log.warning("could not fetch dexscreener trending: %s", e)
        return []
    return [
        p["tokenAddress"]
        for p in profiles
        if isinstance(p, dict) and p.get("chainId") == "solana" and p.get("tokenAddress")
    ][:limit]


def _default_curated_path(data_dir: str) -> str:
    return os.path.join(data_dir, "smart_money_curated.json")


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="meridian.datafeed.smart_money.refresh")
    ap.add_argument("--curated", default=None,
                    help="path to curated wallets JSON (default: <DATA_DIR>/smart_money_curated.json)")
    ap.add_argument("--min-appearances", type=int, default=2,
                    help="reject discovered wallets seen on fewer than N winners")
    ap.add_argument("--max-winners", type=int, default=20,
                    help="how many candidate winner tokens to query per source")
    ap.add_argument("--helius-per-token", type=int, default=30,
                    help="earliest buyers to pull per winner from Helius")
    ap.add_argument("--birdeye-per-token", type=int, default=10,
                    help="top traders to pull per winner from Birdeye (max 10)")
    ap.add_argument("--birdeye-throttle-s", type=float, default=1.1,
                    help="sleep between Birdeye calls (Standard tier = 1 RPS)")
    ap.add_argument("--helius-throttle-s", type=float, default=0.15,
                    help="sleep between Helius calls")
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="emit DEBUG-level logs (default is INFO)")
    args = ap.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    # httpx's INFO logger emits the full request URL — which for Helius
    # includes ?api-key=<secret>. Suppress at INFO so the key never lands in
    # logs, console, or CI artefacts. Promoted to DEBUG when -v is passed.
    logging.getLogger("httpx").setLevel(
        logging.DEBUG if args.verbose else logging.WARNING
    )

    settings = get_settings()
    helius_key = os.getenv("HELIUS_API_KEY", "").strip()
    birdeye_key = os.getenv("BIRDEYE_API_KEY", "").strip()
    curated_path = args.curated or _default_curated_path(settings.data_dir)

    if not helius_key and not birdeye_key:
        log.warning("neither HELIUS_API_KEY nor BIRDEYE_API_KEY is set; only curated source will be loaded")

    winners = _winners_from_dexscreener_trending(args.max_winners)
    log.info("discovering against %d candidate winner tokens", len(winners))

    wallets = discover.discover_wallets(
        winner_mints=winners,
        helius_key=helius_key or None,
        birdeye_key=birdeye_key or None,
        curated_path=curated_path,
        helius_per_token_limit=args.helius_per_token,
        birdeye_per_token_limit=args.birdeye_per_token,
        birdeye_throttle_s=args.birdeye_throttle_s,
        helius_throttle_s=args.helius_throttle_s,
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
