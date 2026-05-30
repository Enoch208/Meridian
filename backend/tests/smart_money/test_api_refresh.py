"""POST /api/smart-money/refresh — auth gate + background task wiring."""
from fastapi.testclient import TestClient

from meridian.api.server import create_app


def test_returns_403_without_secret(tmp_path, monkeypatch):
    monkeypatch.setenv("MERIDIAN_RUN_SECRET", "topsecret")
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setenv("MONGODB_URI", "")
    client = TestClient(create_app())
    r = client.post("/api/smart-money/refresh")
    assert r.status_code == 403


def test_returns_403_with_wrong_secret(tmp_path, monkeypatch):
    monkeypatch.setenv("MERIDIAN_RUN_SECRET", "topsecret")
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setenv("MONGODB_URI", "")
    client = TestClient(create_app())
    r = client.post("/api/smart-money/refresh", headers={"x-run-secret": "wrong"})
    assert r.status_code == 403


def test_queues_when_secret_matches(tmp_path, monkeypatch):
    monkeypatch.setenv("MERIDIAN_RUN_SECRET", "topsecret")
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setenv("MONGODB_URI", "")
    # No source keys → background task degrades to curated-only (empty) and exits cleanly.
    monkeypatch.setenv("HELIUS_API_KEY", "")
    monkeypatch.setenv("BIRDEYE_API_KEY", "")
    client = TestClient(create_app())
    r = client.post("/api/smart-money/refresh", headers={"x-run-secret": "topsecret"})
    assert r.status_code == 200
    assert r.json() == {"status": "queued"}


def test_empty_secret_denies_all(tmp_path, monkeypatch):
    """Unset run_secret means deny everything — never accept a missing secret."""
    monkeypatch.setenv("MERIDIAN_RUN_SECRET", "")
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setenv("MONGODB_URI", "")
    client = TestClient(create_app())
    r = client.post("/api/smart-money/refresh", headers={"x-run-secret": ""})
    assert r.status_code == 403
