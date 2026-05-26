from meridian.datafeed.models import Candidate, UNKNOWN


def test_ratios_and_unknown():
    c = Candidate(address="A", name="n", symbol="S", pair_url="u",
                  buys_h1=30, sells_h1=10, liquidity_usd=5000, fdv=50000)
    assert c.buy_sell_ratio_h1() == 3.0
    assert c.liq_to_fdv() == 0.1
    assert c.mint_authority == UNKNOWN
    bare = Candidate(address="A", name="n", symbol="S", pair_url="u")
    assert bare.buy_sell_ratio_h1() is None
    assert bare.liq_to_fdv() is None
