"""Tests for the Jupiter token-search parser (pure, no network)."""
from meridian.datafeed.jupiter import parse_market


def test_parse_market_extracts_fields():
    data = [
        {
            "id": "MINT",
            "name": "X",
            "symbol": "X",
            "usdPrice": 0.0000031,
            "liquidity": 653.09,
            "fdv": 3000,
            "mcap": 3000,
            "icon": "https://img",
            "holderCount": 19,
            "launchpad": "swarms.world",
            "stats1h": {"numBuys": 9, "numSells": 1},
            "stats24h": {"priceChange": 110.2},
        }
    ]
    out = parse_market(data, "MINT")
    assert out["usd_price"] == 0.0000031
    assert out["liquidity_usd"] == 653.09
    assert out["icon"] == "https://img"
    assert out["holder_count"] == 19
    assert out["price_change_24h"] == 110.2
    assert out["buys_1h"] == 9 and out["sells_1h"] == 1


def test_parse_market_missing_or_garbage():
    assert parse_market([], "MINT") is None
    assert parse_market([{"id": "OTHER", "usdPrice": 1}], "MINT") is None
    assert parse_market("nope", "MINT") is None
    # dict shape (old price/v3) is no longer accepted
    assert parse_market({"MINT": {"usdPrice": 1}}, "MINT") is None
