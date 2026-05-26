import json
import pathlib

from meridian.run import main


def test_run_writes_artifact_and_logs(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    picks = main(["--mock", "--demo"])
    assert len(picks) >= 1

    artifact = pathlib.Path(tmp_path) / "latest_shortlist.json"
    assert artifact.exists()
    data = json.loads(artifact.read_text())
    assert data["picks"] and data["disclaimer"]
    assert data["picks"][0]["scores"]["smart_money"] is None

    assert (pathlib.Path(tmp_path) / "calls.jsonl").exists()


def test_artifact_roundtrips_through_api(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient
    from meridian.api.server import create_app

    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    main(["--mock", "--demo"])
    client = TestClient(create_app())
    body = client.get("/api/daily-shortlist").json()
    assert len(body["picks"]) >= 1
    assert body["generated_at"]
