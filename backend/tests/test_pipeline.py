from meridian.pipeline import run_pipeline
from meridian.scouts.swarm import MockScoutSwarm
from meridian.datafeed.models import Candidate


def test_pipeline_end_to_end():
    cands = [
        Candidate(address="a", name="n", symbol="GOOD", pair_url="u", liquidity_usd=9000,
                  mint_authority="renounced", freeze_authority="renounced", buys_h1=30, sells_h1=10),
        Candidate(address="b", name="n", symbol="LOW", pair_url="u", liquidity_usd=10),
    ]
    picks = run_pipeline(MockScoutSwarm(), fetch=lambda: cands,
                         enrich=lambda cs, url: cs, min_liquidity_usd=5000)
    assert [p.candidate.symbol for p in picks] == ["GOOD"]


def test_pipeline_empty_when_all_filtered():
    cands = [Candidate(address="b", name="n", symbol="LOW", pair_url="u", liquidity_usd=10)]
    picks = run_pipeline(MockScoutSwarm(), fetch=lambda: cands,
                         enrich=lambda cs, url: cs, min_liquidity_usd=5000)
    assert picks == []
