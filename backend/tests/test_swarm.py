import os

import pytest

from meridian.datafeed.models import Candidate
from meridian.scouts.swarm import MockScoutSwarm, to_agent_payload, parse_lead_json


def _cands():
    return [Candidate(address=str(i), name="n", symbol=f"S{i}", pair_url="u",
                      liquidity_usd=10000 * i, buys_h1=20, sells_h1=5,
                      mint_authority="renounced", freeze_authority="renounced")
            for i in (1, 2, 3)]


def test_mock_swarm_ranks():
    picks = MockScoutSwarm().rank(_cands())
    assert len(picks) == 3 and picks[0].rank == 1
    assert picks[0].scores["smart_money"] is None
    assert "smart_money" in picks[0].unknowns
    # highest liquidity ranks first
    assert picks[0].candidate.symbol == "S3"


def test_to_agent_payload_marks_unknown():
    c = Candidate(address="a", name="n", symbol="S", pair_url="u", liquidity_usd=5000)
    p = to_agent_payload(c)
    assert p["liquidity_usd"] == 5000
    assert p["volume_h24"] == "Unknown"  # None -> Unknown
    assert p["mint_authority"] == "Unknown"


def test_parse_lead_json_handles_fences():
    cands = _cands()
    text = """Here you go:
```json
[{"rank":1,"symbol":"S2","composite_score":80,
  "scores":{"onchain":70,"liquidity":85,"momentum":80,"smart_money":null},
  "top_reasons":["liquid","buyers"],"standout_risk":"young","one_line_read":"worth a look",
  "unknowns":["smart_money"]}]
```"""
    picks = parse_lead_json(text, cands)
    assert len(picks) == 1
    assert picks[0].candidate.symbol == "S2"
    assert picks[0].composite_score == 80
    assert picks[0].scores["smart_money"] is None


@pytest.mark.skipif(os.getenv("RUN_LIVE_SWARM") != "1", reason="set RUN_LIVE_SWARM=1 to spend Swarms credit")
def test_live_swarm_smoke():
    from meridian.scouts.swarm import SwarmsScoutSwarm
    picks = SwarmsScoutSwarm().rank(_cands())
    assert 1 <= len(picks) <= 3
    assert all(p.candidate.symbol for p in picks)
