"""Tests for the Telegram bot's pure formatters (no network)."""
from meridian.bot import format_evaluate, format_picks, format_track


def test_format_picks_empty():
    out = format_picks({"picks": []})
    assert "No shortlist yet" in out


def test_format_picks_renders_each_pick():
    data = {
        "as_of_date": "2026-05-26",
        "picks": [
            {
                "rank": 1,
                "token": {"symbol": "NOVA"},
                "composite_score": 87,
                "top_reasons": ["LP 100% locked"],
                "standout_risk": "Very young pair",
                "one_line_read": "Clean and early.",
            },
            {
                "rank": 2,
                "token": {"symbol": "ORBT"},
                "composite_score": 82,
                "top_reasons": ["Volume steepening"],
                "standout_risk": "Thin liquidity",
                "one_line_read": "Momentum building.",
            },
        ],
    }
    out = format_picks(data)
    assert "$NOVA" in out and "87/100" in out
    assert "$ORBT" in out and "82/100" in out
    assert "2026-05-26" in out
    assert "financial advice" in out


def test_format_picks_escapes_html():
    data = {"picks": [{
        "rank": 1, "token": {"symbol": "X"}, "composite_score": 50,
        "top_reasons": ["a < b & c"], "standout_risk": "", "one_line_read": "",
    }]}
    out = format_picks(data)
    assert "&lt; b &amp; c" in out  # raw <, & never leak into HTML


def test_format_track_empty():
    assert "empty" in format_track({"summary": {"total_calls": 0}})


def test_format_evaluate_found():
    data = {
        "found": True,
        "pick": {
            "token": {"symbol": "NOVA", "name": "Nova"},
            "composite_score": 78,
            "scores": {"onchain": 80, "liquidity": 75, "momentum": 70, "smart_money": None},
            "top_reasons": ["LP locked"],
            "standout_risk": "Young pair",
            "one_line_read": "Clean and early.",
        },
        "security": {
            "is_honeypot": False, "buy_tax": 1.0, "sell_tax": 2.0, "overall_score": 80,
        },
    }
    out = format_evaluate(data)
    assert "$NOVA" in out and "78/100" in out
    assert "Young pair" in out and "Smart-money —" in out
    assert "not a honeypot" in out and "safety 80/100" in out


def test_format_evaluate_not_found():
    assert "No Solana pair" in format_evaluate({"found": False})
    assert "boom" in format_evaluate({"found": False, "error": "boom"})


def test_format_track_summary_and_calls():
    data = {
        "summary": {"total_calls": 3, "hits": 1, "misses": 1, "open": 1, "hit_rate": 0.5},
        "calls": [
            {"token": {"symbol": "PULSE"}, "status": "hit", "score_at_call": 84, "date": "2026-05-25"},
            {"token": {"symbol": "VOID"}, "status": "miss", "score_at_call": 66, "date": "2026-05-24"},
        ],
    }
    out = format_track(data)
    assert "Hit rate: <b>50%</b>" in out
    assert "▲ $PULSE" in out
    assert "▼ $VOID" in out
