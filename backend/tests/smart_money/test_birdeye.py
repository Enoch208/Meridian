import json
import pathlib

from meridian.datafeed.smart_money.birdeye import parse_top_traders


FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "birdeye_top_traders.json"


def test_parse_top_traders_maps_fields():
    resp = json.loads(FIXTURE.read_text())
    obs = parse_top_traders(resp, mint="WIN_MINT")

    assert [o.address for o in obs] == ["WHALE_1", "WHALE_2", "WHALE_3"]
    assert [o.rank for o in obs] == [1, 2, 3]
    assert obs[0].volume_usd == 120000
    assert obs[0].trade_count == 24
    assert obs[0].pnl_usd == 18000
    assert obs[2].pnl_usd == -1200
    assert all(o.source == "birdeye:top_traders" for o in obs)
    assert all(o.token_mint == "WIN_MINT" for o in obs)


def test_parse_top_traders_accepts_list_payload():
    # Some Birdeye endpoints return data as a list directly.
    resp = {"data": [{"owner": "A", "volume": 100}]}
    obs = parse_top_traders(resp, mint="M")
    assert obs and obs[0].address == "A"


def test_parse_top_traders_handles_garbage():
    assert parse_top_traders({}, mint="M") == []
    assert parse_top_traders({"data": None}, mint="M") == []
    assert parse_top_traders({"data": {"items": [{"no_owner": "x"}]}}, mint="M") == []
