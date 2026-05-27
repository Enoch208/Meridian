"""Tests for the token security-check parser (pure, no network)."""
from meridian.datafeed.tokencheck import extract


def test_extract_pulls_key_fields():
    raw = {
        "honeypotDetails": {
            "overAllScore": 82,
            "isPairHoneypot": 0,
            "honeypotReason": "",
            "buyTax": {"number": 1.5},
            "sellTax": {"number": 2.0},
            "transferTax": 0,
        },
        "codeChecks": {"codeCheckScore": 70},
        "marketChecks": {"marketCheckScore": 65, "lockedLiquidityPercent": 88},
    }
    out = extract(raw)
    assert out["overall_score"] == 82
    assert out["is_honeypot"] is False
    assert out["buy_tax"] == 1.5 and out["sell_tax"] == 2.0
    assert out["code_score"] == 70 and out["market_score"] == 65
    assert out["liquidity_locked_pct"] == 88


def test_extract_flags_honeypot():
    out = extract({"honeypotDetails": {"isPairHoneypot": 1}})
    assert out["is_honeypot"] is True


def test_extract_handles_garbage():
    assert extract(None) is None
    assert extract("nope") is None
    assert extract({}) is None  # nothing parses → treated as no data
