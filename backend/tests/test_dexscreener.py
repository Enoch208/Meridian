import json
import pathlib

from meridian.datafeed.dexscreener import parse_token_pairs


def test_parse_picks_best_pair():
    raw = json.loads(
        (pathlib.Path(__file__).parent / "fixtures/dexscreener_tokens.json").read_text()
    )
    cands = parse_token_pairs(raw)
    assert cands and cands[0].symbol
    assert cands[0].liquidity_usd is not None
    assert cands[0].pair_url.startswith("http")
