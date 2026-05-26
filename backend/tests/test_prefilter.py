from meridian.scoring.prefilter import prefilter
from meridian.datafeed.models import Candidate


def test_prefilter():
    low = Candidate(address="a", name="", symbol="LOW", pair_url="", liquidity_usd=100)
    rug = Candidate(address="b", name="", symbol="RUG", pair_url="", liquidity_usd=9000,
                    mint_authority="live:x", freeze_authority="live:y")
    ok  = Candidate(address="c", name="", symbol="OK", pair_url="", liquidity_usd=9000,
                    mint_authority="renounced", freeze_authority="renounced")
    kept, drops = prefilter([low, rug, ok], min_liquidity_usd=5000)
    assert [c.symbol for c in kept] == ["OK"]
    assert {s for s, _ in drops} == {"LOW", "RUG"}
