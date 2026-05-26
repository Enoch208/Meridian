"""Tests for trackrecord/update.py — Task 11."""
import json
import pathlib

from meridian.trackrecord.update import recompute_status, update_all


def test_recompute_status():
    c = {"price_at_call_usd": 0.001, "status": "open"}
    # 60% gain → hit (>= 50%)
    assert recompute_status(c, price_now=0.0016)["status"] == "hit"
    # -60% → miss (<= -50%)
    assert recompute_status(c, price_now=0.0004)["status"] == "miss"
    # +10% → stays open
    assert recompute_status(c, price_now=0.0011)["status"] == "open"


def test_recompute_status_boundary_values():
    c = {"price_at_call_usd": 0.001, "status": "open"}
    # Exactly +50% → hit
    result = recompute_status(c, price_now=0.0015)
    assert result["status"] == "hit"
    assert abs(result["pct_change"] - 50.0) < 1e-9
    # Exactly -50% → miss
    result = recompute_status(c, price_now=0.0005)
    assert result["status"] == "miss"
    assert abs(result["pct_change"] - (-50.0)) < 1e-9


def test_recompute_does_not_mutate_original():
    """recompute_status returns a new dict, the original is unchanged."""
    original = {"price_at_call_usd": 0.001, "status": "open", "score_at_call": 80}
    result = recompute_status(original, price_now=0.002)
    # Original not modified
    assert original["status"] == "open"
    assert "pct_change" not in original
    # Result has updated fields
    assert result["status"] == "hit"
    assert result["score_at_call"] == 80  # preserved


def test_update_all_writes_track_record_json(tmp_path):
    """update_all writes track-record.json and uses price_lookup."""
    calls_data = [
        {"date": "2026-01-01", "rank": 1,
         "token": {"name": "A", "symbol": "A", "address": "addr_a"},
         "score_at_call": 80, "price_at_call_usd": 0.001,
         "price_now_usd": None, "pct_change": None, "status": "open"},
    ]
    p = pathlib.Path(tmp_path) / "calls.jsonl"
    p.write_text("\n".join(json.dumps(c) for c in calls_data) + "\n")

    # price_lookup: addr_a → 0.002 (100% gain → hit)
    update_all(str(tmp_path), price_lookup=lambda addr: 0.002)

    out = pathlib.Path(tmp_path) / "track-record.json"
    assert out.exists()
    data = json.loads(out.read_text())
    assert data["summary"]["hits"] == 1
    assert data["calls"][0]["status"] == "hit"
    assert abs(data["calls"][0]["pct_change"] - 100.0) < 1e-9


def test_update_all_does_not_mutate_calls_jsonl(tmp_path):
    """update_all must NOT change calls.jsonl."""
    calls_data = [
        {"date": "2026-01-01", "rank": 1,
         "token": {"name": "A", "symbol": "A", "address": "addr_a"},
         "score_at_call": 80, "price_at_call_usd": 0.001,
         "price_now_usd": None, "pct_change": None, "status": "open"},
    ]
    p = pathlib.Path(tmp_path) / "calls.jsonl"
    original_content = "\n".join(json.dumps(c) for c in calls_data) + "\n"
    p.write_text(original_content)

    update_all(str(tmp_path), price_lookup=lambda addr: 0.002)

    # calls.jsonl content must be byte-for-byte identical
    assert p.read_text() == original_content


def test_update_all_price_lookup_returns_none(tmp_path):
    """When price_lookup returns None (unknown price), status stays open."""
    calls_data = [
        {"date": "2026-01-01", "rank": 1,
         "token": {"name": "A", "symbol": "A", "address": "addr_a"},
         "score_at_call": 80, "price_at_call_usd": 0.001,
         "price_now_usd": None, "pct_change": None, "status": "open"},
    ]
    p = pathlib.Path(tmp_path) / "calls.jsonl"
    p.write_text("\n".join(json.dumps(c) for c in calls_data) + "\n")

    update_all(str(tmp_path), price_lookup=lambda addr: None)

    out = pathlib.Path(tmp_path) / "track-record.json"
    data = json.loads(out.read_text())
    assert data["calls"][0]["status"] == "open"
    assert data["calls"][0]["price_now_usd"] is None
