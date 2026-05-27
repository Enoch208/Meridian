"""Tests for the Jupiter price/v3 parser (pure, no network)."""
from meridian.datafeed.jupiter import parse_market


def test_parse_market_extracts_fields():
    data = {
        "MINT": {
            "usdPrice": 0.0000031,
            "liquidity": 653.09,
            "priceChange24h": 110.2,
            "decimals": 6,
            "launchpad": "swarms.world",
        }
    }
    out = parse_market(data, "MINT")
    assert out["usd_price"] == 0.0000031
    assert out["liquidity_usd"] == 653.09
    assert out["price_change_24h"] == 110.2


def test_parse_market_missing_or_garbage():
    assert parse_market({}, "MINT") is None
    assert parse_market({"OTHER": {"usdPrice": 1}}, "MINT") is None
    assert parse_market("nope", "MINT") is None
    # entry present but no usable numbers → None
    assert parse_market({"MINT": {"decimals": 6}}, "MINT") is None
