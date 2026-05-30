import json
import pathlib

from meridian.datafeed.smart_money.helius import parse_buyers_from_swaps


FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "helius_swaps.json"


def test_parse_buyers_deduplicates_and_ranks():
    txns = json.loads(FIXTURE.read_text())
    obs = parse_buyers_from_swaps(txns, mint="MINT_X")

    # BUYER_A first, BUYER_B second, BUYER_C third — dedup drops repeat A,
    # rando swap on a different mint is ignored entirely.
    assert [o.address for o in obs] == ["BUYER_A", "BUYER_B", "BUYER_C"]
    assert [o.rank for o in obs] == [1, 2, 3]
    assert all(o.token_mint == "MINT_X" for o in obs)
    assert all(o.source == "helius:earliest_buyers" for o in obs)
    assert obs[0].buy_timestamp == 1716000000


def test_parse_buyers_handles_garbage_input():
    assert parse_buyers_from_swaps([], mint="MINT_X") == []
    assert parse_buyers_from_swaps("not a list", mint="MINT_X") == []  # type: ignore[arg-type]
    assert parse_buyers_from_swaps([{"tokenTransfers": []}], mint="MINT_X") == []
