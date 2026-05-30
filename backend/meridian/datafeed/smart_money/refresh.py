"""Refresh the smart-money watchlist.

CLI:
    python -m meridian.datafeed.smart_money.refresh
    python -m meridian.datafeed.smart_money.refresh --max-winners 15 -v

Library:
    from meridian.datafeed.smart_money.refresh import run_refresh
    wallets = run_refresh()

Reads HELIUS_API_KEY and BIRDEYE_API_KEY from the environment. If neither is
set, only the curated source is loaded.
"""
from __future__ import annotations

import argparse
import logging
import os
import pathlib
from dataclasses import dataclass
from typing import Optional

import httpx

from meridian.config import get_settings

from . import cache, discover, watchlist
from .models import SmartMoneyWallet

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class RefreshOptions:
    max_winners: int = 20
    min_appearances: int = 2
    helius_per_token_limit: int = 30
    birdeye_per_token_limit: int = 10
    birdeye_throttle_s: float = 1.1
    helius_throttle_s: float = 0.15
    cache_ttl_s: int = cache.DEFAULT_TTL_S
    curated_path: Optional[str] = None     # default: <DATA_DIR>/smart_money_curated.json


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


def run_refresh(opts: RefreshOptions = RefreshOptions()) -> list[SmartMoneyWallet]:
    """Library entrypoint — shared by the CLI and the /api/smart-money/refresh route.

    Reads keys + Mongo config from env via ``get_settings``. Writes the result
    to whichever backend ``save_watchlist`` selects (Mongo if ``MONGODB_URI``
    is set, JSON file otherwise). Uses the on-disk cache to skip per-mint API
    calls that have run in the last hour.
    """
    settings = get_settings()
    helius_key = os.getenv("HELIUS_API_KEY", "").strip() or None
    birdeye_key = os.getenv("BIRDEYE_API_KEY", "").strip() or None
    curated_path = opts.curated_path or os.path.join(settings.data_dir, "smart_money_curated.json")

    if not helius_key and not birdeye_key:
        log.warning("neither HELIUS_API_KEY nor BIRDEYE_API_KEY is set; only curated source will be loaded")

    winners = _winners_from_dexscreener_trending(opts.max_winners)
    log.info("discovering against %d candidate winner tokens", len(winners))

    wallets = discover.discover_wallets(
        winner_mints=winners,
        helius_key=helius_key,
        birdeye_key=birdeye_key,
        curated_path=curated_path,
        helius_per_token_limit=opts.helius_per_token_limit,
        birdeye_per_token_limit=opts.birdeye_per_token_limit,
        birdeye_throttle_s=opts.birdeye_throttle_s,
        helius_throttle_s=opts.helius_throttle_s,
        min_appearances=opts.min_appearances,
        cache_dir=settings.data_dir,           # share <DATA_DIR>/cache/
        cache_ttl_s=opts.cache_ttl_s,
    )
    pathlib.Path(settings.data_dir).mkdir(parents=True, exist_ok=True)
    watchlist.save_watchlist(wallets, settings.data_dir)
    log.info(
        "wrote %d wallets to %s",
        len(wallets), "MongoDB" if settings.mongodb_uri else settings.data_dir,
    )
    return wallets


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="meridian.datafeed.smart_money.refresh")
    ap.add_argument("--curated", default=None,
                    help="path to curated wallets JSON (default: <DATA_DIR>/smart_money_curated.json)")
    ap.add_argument("--min-appearances", type=int, default=2)
    ap.add_argument("--max-winners", type=int, default=20)
    ap.add_argument("--helius-per-token", type=int, default=30)
    ap.add_argument("--birdeye-per-token", type=int, default=10)
    ap.add_argument("--birdeye-throttle-s", type=float, default=1.1)
    ap.add_argument("--helius-throttle-s", type=float, default=0.15)
    ap.add_argument("--cache-ttl-s", type=int, default=cache.DEFAULT_TTL_S,
                    help="seconds before a cached source response is considered stale")
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

    wallets = run_refresh(RefreshOptions(
        max_winners=args.max_winners,
        min_appearances=args.min_appearances,
        helius_per_token_limit=args.helius_per_token,
        birdeye_per_token_limit=args.birdeye_per_token,
        birdeye_throttle_s=args.birdeye_throttle_s,
        helius_throttle_s=args.helius_throttle_s,
        cache_ttl_s=args.cache_ttl_s,
        curated_path=args.curated,
    ))

    print(f"Identified {len(wallets)} smart-money wallets.")
    for w in wallets[:10]:
        masked = f"{w.address[:6]}…{w.address[-4:]}" if len(w.address) > 12 else w.address
        rank_str = f"  avg_rank={w.avg_entry_rank:.1f}" if w.avg_entry_rank else ""
        print(
            f"  {masked}  score={w.score:5.1f}  winners={w.winners_caught}"
            f"{rank_str}  sources={w.sources}"
        )

    settings = get_settings()
    store = "MongoDB" if settings.mongodb_uri else settings.data_dir
    print(f"Saved watchlist to {store}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
