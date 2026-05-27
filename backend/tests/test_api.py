"""Tests for api/server.py — Task 12."""
import json
import pathlib

from fastapi.testclient import TestClient
from meridian.api.server import create_app


def test_endpoints(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    client = TestClient(create_app())
    assert client.get("/health").json()["status"] == "ok"
    body = client.get("/api/daily-shortlist").json()
    assert "picks" in body and body["disclaimer"]
    assert client.get("/api/track-record").json()["summary"]["total_calls"] == 0


def test_health_endpoint(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    client = TestClient(create_app())
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_daily_shortlist_missing_file(tmp_path, monkeypatch):
    """When latest_shortlist.json is absent, return 200 with picks=[] and generated_at=null."""
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    client = TestClient(create_app())
    resp = client.get("/api/daily-shortlist")
    assert resp.status_code == 200
    body = resp.json()
    assert body["picks"] == []
    assert body["generated_at"] is None
    assert body["disclaimer"]  # non-empty disclaimer
    assert "data_source" in body
    assert "as_of_date" in body
    assert "free_tier_cutoff" in body


def test_daily_shortlist_with_data(tmp_path, monkeypatch):
    """When latest_shortlist.json exists, it is returned as-is (picks non-empty)."""
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    shortlist = {
        "generated_at": "2026-05-26T18:00:00Z",
        "as_of_date": "2026-05-26",
        "data_source": "dexscreener+solana-rpc",
        "disclaimer": "Not financial advice.",
        "free_tier_cutoff": 1,
        "picks": [
            {
                "rank": 1,
                "token": {"name": "Example", "symbol": "EXMPL",
                          "address": "So1ana", "pair_url": "https://dex.com"},
                "composite_score": 78,
                "scores": {"onchain": 70, "liquidity": 85, "momentum": 80, "smart_money": None},
                "top_reasons": ["High liquidity"],
                "standout_risk": "New pair",
                "one_line_read": "Worth a look.",
                "metrics": {
                    "liquidity_usd": 41200, "fdv": 180000, "age_hours": 4,
                    "volume_h24": 95000, "buy_sell_ratio_h1": 3.1,
                    "mint_authority": "renounced", "freeze_authority": "renounced",
                },
                "unknowns": ["smart_money"],
            }
        ],
    }
    (pathlib.Path(tmp_path) / "latest_shortlist.json").write_text(json.dumps(shortlist))

    client = TestClient(create_app())
    resp = client.get("/api/daily-shortlist")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["picks"]) == 1
    assert body["picks"][0]["rank"] == 1
    assert body["picks"][0]["token"]["symbol"] == "EXMPL"


def test_track_record_empty(tmp_path, monkeypatch):
    """When no calls.jsonl, track-record summary has all-zero counts."""
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    client = TestClient(create_app())
    resp = client.get("/api/track-record")
    assert resp.status_code == 200
    body = resp.json()
    assert "updated_at" in body
    assert "summary" in body
    assert "calls" in body
    summary = body["summary"]
    assert summary["total_calls"] == 0
    assert summary["hits"] == 0
    assert summary["misses"] == 0
    assert summary["open"] == 0
    assert summary["hit_rate"] is None


def test_track_record_with_calls(tmp_path, monkeypatch):
    """track-record reflects appended calls."""
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    calls_data = [
        {"date": "2026-01-01", "rank": 1,
         "token": {"name": "A", "symbol": "A", "address": "A"},
         "score_at_call": 80, "price_at_call_usd": 0.001,
         "price_now_usd": 0.002, "pct_change": 100.0, "status": "hit"},
    ]
    (pathlib.Path(tmp_path) / "calls.jsonl").write_text(
        "\n".join(json.dumps(c) for c in calls_data) + "\n"
    )

    client = TestClient(create_app())
    resp = client.get("/api/track-record")
    assert resp.status_code == 200
    body = resp.json()
    assert body["summary"]["total_calls"] == 1
    assert body["summary"]["hits"] == 1
    assert len(body["calls"]) == 1


def test_run_endpoint_wrong_secret(tmp_path, monkeypatch):
    """POST /api/run with wrong secret returns 403."""
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setenv("MERIDIAN_RUN_SECRET", "correct-secret")
    client = TestClient(create_app())
    resp = client.post("/api/run", headers={"x-run-secret": "wrong"})
    assert resp.status_code == 403


def test_run_endpoint_correct_secret(tmp_path, monkeypatch):
    """POST /api/run with correct secret returns queued and schedules a live run.

    The real pipeline is monkeypatched so no network call / credit is spent —
    we only assert the endpoint wires the background task to the live run.
    """
    import meridian.run as run_mod

    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setenv("MERIDIAN_RUN_SECRET", "correct-secret")

    invoked = {}

    def fake_main(argv=None):
        invoked["argv"] = argv
        return []

    monkeypatch.setattr(run_mod, "main", fake_main)

    client = TestClient(create_app())
    resp = client.post("/api/run", headers={"x-run-secret": "correct-secret"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "queued"
    # The background task ran the live pipeline exactly once, in --live mode.
    assert invoked.get("argv") == ["--live"]


def test_run_endpoint_no_secret_configured(tmp_path, monkeypatch):
    """When run_secret is empty, any request is denied (empty secret matches nothing meaningful)."""
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setenv("MERIDIAN_RUN_SECRET", "")
    client = TestClient(create_app())
    # Sending any non-empty secret against an empty configured secret should 403
    resp = client.post("/api/run", headers={"x-run-secret": "something"})
    assert resp.status_code == 403


def test_evaluate_scores_a_token(tmp_path, monkeypatch):
    """POST /api/evaluate fetches + scores a single token (network mocked)."""
    from meridian.datafeed import dexscreener, enrich
    from meridian.datafeed.models import Candidate

    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    cand = Candidate(
        address="X", name="Test", symbol="TST", pair_url="u",
        liquidity_usd=50000, fdv=200000, market_cap=190000, age_hours=10,
        volume_h24=80000, volume_h6=30000, volume_h1=9000, buys_h1=80, sells_h1=40,
        price_usd=0.001, mint_authority="renounced", freeze_authority="renounced",
    )
    monkeypatch.setattr(dexscreener, "fetch_token", lambda addr, client=None: [cand])
    monkeypatch.setattr(enrich, "enrich_authorities", lambda cands, rpc: cands)

    client = TestClient(create_app())
    resp = client.post("/api/evaluate", json={"token": "X"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["found"] is True
    assert body["pick"]["token"]["symbol"] == "TST"
    assert isinstance(body["pick"]["composite_score"], int)
    assert body["pick"]["standout_risk"]


def test_evaluate_fills_liquidity_from_jupiter(tmp_path, monkeypatch):
    """When DexScreener has no liquidity, Jupiter fills it (no longer Unknown)."""
    from meridian.datafeed import dexscreener, enrich, jupiter
    from meridian.datafeed.models import Candidate

    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    cand = Candidate(
        address="X", name="T", symbol="TST", pair_url="u",
        liquidity_usd=None, fdv=3000, age_hours=10,
        volume_h24=900, buys_h1=9, sells_h1=1, price_usd=None,
        mint_authority="renounced", freeze_authority="renounced",
    )
    monkeypatch.setattr(dexscreener, "fetch_token", lambda a, client=None: [cand])
    monkeypatch.setattr(enrich, "enrich_authorities", lambda c, rpc: c)
    monkeypatch.setattr(
        jupiter, "fetch_market",
        lambda mint: {"liquidity_usd": 653.0, "usd_price": 0.000003, "price_change_24h": 110.0},
    )

    client = TestClient(create_app())
    body = client.post("/api/evaluate", json={"token": "X"}).json()
    assert body["found"] is True
    assert body["pick"]["metrics"]["liquidity_usd"] == 653.0
    assert body["pick"]["scores"]["liquidity"] is not None  # filled, not Unknown


def test_evaluate_includes_security_when_available(tmp_path, monkeypatch):
    """When the security check returns data, it's attached to the response."""
    from meridian.datafeed import dexscreener, enrich, tokencheck
    from meridian.datafeed.models import Candidate

    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    cand = Candidate(
        address="X", name="T", symbol="TST", pair_url="u",
        liquidity_usd=50000, fdv=200000, market_cap=190000, age_hours=10,
        volume_h24=80000, volume_h6=30000, volume_h1=9000, buys_h1=80, sells_h1=40,
        price_usd=0.001, mint_authority="renounced", freeze_authority="renounced",
    )
    monkeypatch.setattr(dexscreener, "fetch_token", lambda a, client=None: [cand])
    monkeypatch.setattr(enrich, "enrich_authorities", lambda c, rpc: c)
    monkeypatch.setattr(
        tokencheck, "fetch_security",
        lambda addr: {"is_honeypot": False, "buy_tax": 1.0, "overall_score": 80},
    )

    client = TestClient(create_app())
    body = client.post("/api/evaluate", json={"token": "X"}).json()
    assert body["found"] is True
    assert body["security"]["is_honeypot"] is False
    assert body["security"]["buy_tax"] == 1.0


def test_evaluate_not_found(tmp_path, monkeypatch):
    """Unknown token → found=False, 200 (graceful)."""
    from meridian.datafeed import dexscreener

    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setattr(dexscreener, "fetch_token", lambda addr, client=None: [])
    client = TestClient(create_app())
    resp = client.post("/api/evaluate", json={"token": "nope"})
    assert resp.status_code == 200 and resp.json()["found"] is False


def test_cors_headers_present(tmp_path, monkeypatch):
    """CORS allow-all is configured — preflight should be accepted."""
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    client = TestClient(create_app())
    resp = client.options(
        "/health",
        headers={"origin": "http://localhost:3000",
                 "access-control-request-method": "GET"},
    )
    # With permissive CORS we expect at least a 200 response
    assert resp.status_code in (200, 204)
