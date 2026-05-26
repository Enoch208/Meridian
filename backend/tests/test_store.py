"""Tests for trackrecord/store.py — Task 10."""
from meridian.trackrecord.store import append_calls, load_calls, derive_scorecard
from meridian.datafeed.models import Candidate, Pick


def _pick(sym, price):
    c = Candidate(address=sym, name="n", symbol=sym, pair_url="u", price_usd=price)
    return Pick(
        1, c, 80,
        {"onchain": 70, "liquidity": 85, "momentum": 80, "smart_money": None},
        ["r"], "risk", "read", ["smart_money"],
    )


def test_append_and_scorecard(tmp_path):
    append_calls([_pick("A", 0.001)], str(tmp_path))
    append_calls([_pick("B", 0.002)], str(tmp_path))
    calls = load_calls(str(tmp_path))
    assert len(calls) == 2
    sc = derive_scorecard(calls)
    assert sc["summary"]["total_calls"] == 2
    assert sc["summary"]["open"] == 2
    assert sc["summary"]["hit_rate"] is None


def test_load_calls_missing_file(tmp_path):
    """load_calls returns [] when calls.jsonl doesn't exist."""
    calls = load_calls(str(tmp_path))
    assert calls == []


def test_append_only_never_rewrites(tmp_path):
    """Appending a second batch does not overwrite the first."""
    append_calls([_pick("A", 0.001)], str(tmp_path))
    # Manually read the first line to verify it is preserved after a second append.
    import pathlib
    line1_before = (pathlib.Path(tmp_path) / "calls.jsonl").read_text().splitlines()[0]
    append_calls([_pick("B", 0.002)], str(tmp_path))
    line1_after = (pathlib.Path(tmp_path) / "calls.jsonl").read_text().splitlines()[0]
    assert line1_before == line1_after


def test_scorecard_with_hits_and_misses(tmp_path):
    """derive_scorecard computes hit_rate correctly when hits+misses > 0."""
    import json, pathlib

    calls_data = [
        {"date": "2026-01-01", "rank": 1, "token": {"name": "A", "symbol": "A", "address": "A"},
         "score_at_call": 80, "price_at_call_usd": 0.001,
         "price_now_usd": 0.002, "pct_change": 100.0, "status": "hit"},
        {"date": "2026-01-01", "rank": 2, "token": {"name": "B", "symbol": "B", "address": "B"},
         "score_at_call": 70, "price_at_call_usd": 0.002,
         "price_now_usd": 0.001, "pct_change": -50.0, "status": "miss"},
        {"date": "2026-01-02", "rank": 1, "token": {"name": "C", "symbol": "C", "address": "C"},
         "score_at_call": 75, "price_at_call_usd": 0.003,
         "price_now_usd": None, "pct_change": None, "status": "open"},
    ]
    p = pathlib.Path(tmp_path) / "calls.jsonl"
    p.write_text("\n".join(json.dumps(c) for c in calls_data) + "\n")

    calls = load_calls(str(tmp_path))
    sc = derive_scorecard(calls)
    summary = sc["summary"]
    assert summary["total_calls"] == 3
    assert summary["hits"] == 1
    assert summary["misses"] == 1
    assert summary["open"] == 1
    assert abs(summary["hit_rate"] - 0.5) < 1e-9


def test_scorecard_fields_present(tmp_path):
    """derive_scorecard always includes updated_at, summary, and calls keys."""
    sc = derive_scorecard([])
    assert "updated_at" in sc
    assert "summary" in sc
    assert "calls" in sc
    assert sc["summary"]["total_calls"] == 0
    assert sc["summary"]["hit_rate"] is None


def test_call_fields(tmp_path):
    """Each appended call has the required fields."""
    append_calls([_pick("X", 1.5)], str(tmp_path))
    calls = load_calls(str(tmp_path))
    call = calls[0]
    assert call["status"] == "open"
    assert call["price_now_usd"] is None
    assert call["pct_change"] is None
    assert call["score_at_call"] == 80
    assert call["price_at_call_usd"] == 1.5
    assert call["token"]["symbol"] == "X"
    assert "date" in call
    assert "rank" in call
