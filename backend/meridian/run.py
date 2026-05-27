"""CLI entrypoint: generate today's shortlist and log it.

    python -m meridian.run            # mock swarm, live DexScreener data
    python -m meridian.run --live     # real Swarms swarm (spends credit)
    python -m meridian.run --demo     # synthetic candidates, no network
"""
from __future__ import annotations

import argparse
import json
import pathlib
from datetime import datetime, timezone

from meridian.api.schemas import (
    DailyShortlistResponse,
    PickResponse,
    TokenInfo,
    TokenMetrics,
)
from meridian.config import get_settings
from meridian.datafeed.models import Candidate, Pick
from meridian.pipeline import run_pipeline
from meridian.scouts.swarm import MockScoutSwarm
from meridian.trackrecord.store import append_calls, save_shortlist


def _demo_candidates() -> list[Candidate]:
    """Representative offline candidates so the frontend has data immediately."""
    return [
        Candidate(address="DemoMint111", name="Solaris", symbol="SOLR", pair_url="https://dexscreener.com/solana/demo1",
                  liquidity_usd=42000, fdv=180000, market_cap=170000, age_hours=5,
                  volume_h24=96000, volume_h6=51000, volume_h1=14000, buys_h1=120, sells_h1=38,
                  price_usd=0.0021, mint_authority="renounced", freeze_authority="renounced"),
        Candidate(address="DemoMint222", name="Helio", symbol="HELI", pair_url="https://dexscreener.com/solana/demo2",
                  liquidity_usd=28000, fdv=240000, market_cap=230000, age_hours=11,
                  volume_h24=61000, volume_h6=22000, volume_h1=6000, buys_h1=70, sells_h1=44,
                  price_usd=0.0014, mint_authority="renounced", freeze_authority="renounced"),
        Candidate(address="DemoMint333", name="Vega", symbol="VEGA", pair_url="https://dexscreener.com/solana/demo3",
                  liquidity_usd=15000, fdv=90000, market_cap=85000, age_hours=2,
                  volume_h24=33000, volume_h6=19000, volume_h1=8000, buys_h1=95, sells_h1=30,
                  price_usd=0.0009, mint_authority="renounced", freeze_authority="live:Fz9..."),
    ]


def build_shortlist_dict(picks: list[Pick], now: datetime) -> dict:
    resp = DailyShortlistResponse(
        generated_at=now.isoformat(),
        as_of_date=now.date().isoformat(),
        picks=[
            PickResponse(
                rank=p.rank,
                token=TokenInfo(name=p.candidate.name, symbol=p.candidate.symbol,
                                address=p.candidate.address, pair_url=p.candidate.pair_url),
                composite_score=p.composite_score,
                scores=p.scores,
                top_reasons=p.top_reasons,
                standout_risk=p.standout_risk,
                one_line_read=p.one_line_read,
                metrics=TokenMetrics(
                    liquidity_usd=p.candidate.liquidity_usd, fdv=p.candidate.fdv,
                    age_hours=p.candidate.age_hours, volume_h24=p.candidate.volume_h24,
                    buy_sell_ratio_h1=p.candidate.buy_sell_ratio_h1(),
                    mint_authority=p.candidate.mint_authority,
                    freeze_authority=p.candidate.freeze_authority,
                ),
                unknowns=p.unknowns,
            )
            for p in picks
        ],
    )
    return resp.model_dump()


def main(argv: list[str] | None = None) -> list[Pick]:
    ap = argparse.ArgumentParser(prog="meridian.run")
    ap.add_argument("--live", action="store_true", help="use the real Swarms swarm (spends credit)")
    ap.add_argument("--mock", action="store_true", help="use the deterministic mock swarm (default)")
    ap.add_argument("--demo", action="store_true", help="use synthetic candidates (no network)")
    args = ap.parse_args(argv)

    settings = get_settings()

    if args.live:
        from meridian.scouts.swarm import SwarmsScoutSwarm
        swarm = SwarmsScoutSwarm()
    else:
        swarm = MockScoutSwarm()

    fetch = (lambda: _demo_candidates()) if args.demo else None
    enrich = (lambda cs, url: cs) if args.demo else None

    picks = run_pipeline(swarm, fetch=fetch, enrich=enrich)

    now = datetime.now(timezone.utc)
    data_dir = str(settings.data_dir)
    save_shortlist(build_shortlist_dict(picks, now), data_dir)
    append_calls(picks, data_dir, now=now)

    store = "MongoDB" if settings.mongodb_uri else data_dir
    print(f"Wrote {len(picks)} pick(s) to {store}")
    return picks


if __name__ == "__main__":
    main()
