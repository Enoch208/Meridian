"""Orchestration: fetch -> enrich -> prefilter -> swarm.rank.

Dependencies are injectable so the pipeline is testable without network or
Swarms credit (pass a fake ``fetch`` and a ``MockScoutSwarm``).
"""
from __future__ import annotations

from typing import Callable, Optional

from meridian.datafeed.models import Candidate, Pick
from meridian.scoring.prefilter import prefilter
from meridian.scouts.swarm import ScoutSwarm


def run_pipeline(
    swarm: ScoutSwarm,
    *,
    fetch: Optional[Callable[[], list[Candidate]]] = None,
    enrich: Optional[Callable[[list[Candidate], str], list[Candidate]]] = None,
    min_liquidity_usd: Optional[float] = None,
    rpc_url: Optional[str] = None,
) -> list[Pick]:
    from meridian.config import get_settings
    settings = get_settings()

    if fetch is None:
        from meridian.datafeed.dexscreener import fetch_recent_candidates
        fetch = fetch_recent_candidates
    if enrich is None:
        from meridian.datafeed.enrich import enrich_authorities
        enrich = enrich_authorities
    if min_liquidity_usd is None:
        min_liquidity_usd = settings.dex_min_liquidity_usd
    if rpc_url is None:
        rpc_url = settings.solana_rpc_url

    candidates = fetch()
    candidates = enrich(candidates, rpc_url)
    kept, _drops = prefilter(candidates, min_liquidity_usd)
    if not kept:
        return []
    return swarm.rank(kept)
