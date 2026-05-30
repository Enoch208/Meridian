"""File-backed watchlist round-trip + first_seen preservation across upserts."""
import json
import pathlib

from meridian.datafeed.smart_money.models import SmartMoneyWallet
from meridian.datafeed.smart_money.watchlist import (
    WATCHLIST_FILE,
    load_watchlist,
    save_watchlist,
)


def _force_file_backend(monkeypatch, tmp_path):
    # Force the JSON-file backend by clearing MONGODB_URI for these tests.
    monkeypatch.setenv("MONGODB_URI", "")
    monkeypatch.setenv("DATA_DIR", str(tmp_path))


def test_save_load_round_trip(tmp_path, monkeypatch):
    _force_file_backend(monkeypatch, tmp_path)
    wallets = [
        SmartMoneyWallet(address="A", score=85.0, winners_caught=3, sources=["helius:earliest_buyers"]),
        SmartMoneyWallet(address="B", score=60.5, is_curated=True, label="ansem"),
    ]
    save_watchlist(wallets, str(tmp_path))

    loaded = load_watchlist(str(tmp_path))
    by = {w.address: w for w in loaded}
    assert by["A"].score == 85.0
    assert by["B"].label == "ansem" and by["B"].is_curated


def test_first_seen_is_preserved_on_refresh(tmp_path, monkeypatch):
    _force_file_backend(monkeypatch, tmp_path)
    save_watchlist(
        [SmartMoneyWallet(address="STICKY", score=72.0, winners_caught=2)],
        str(tmp_path),
    )
    first_seen = _read(tmp_path)["wallets"][0]["first_seen"]
    assert first_seen

    # Second refresh: score updates, first_seen does NOT.
    save_watchlist(
        [SmartMoneyWallet(address="STICKY", score=88.0, winners_caught=4)],
        str(tmp_path),
    )
    refreshed = _read(tmp_path)["wallets"][0]
    assert refreshed["score"] == 88.0
    assert refreshed["winners_caught"] == 4
    assert refreshed["first_seen"] == first_seen
    assert refreshed["last_seen"] >= first_seen


def test_file_is_sorted_by_score_desc(tmp_path, monkeypatch):
    _force_file_backend(monkeypatch, tmp_path)
    save_watchlist(
        [
            SmartMoneyWallet(address="LOW", score=40.0),
            SmartMoneyWallet(address="HIGH", score=95.0),
            SmartMoneyWallet(address="MID", score=70.0),
        ],
        str(tmp_path),
    )
    scores = [w["score"] for w in _read(tmp_path)["wallets"]]
    assert scores == sorted(scores, reverse=True)


def _read(tmp_path: pathlib.Path) -> dict:
    return json.loads((tmp_path / WATCHLIST_FILE).read_text())
