"""FastAPI application factory.

Use ``create_app()`` rather than a module-level app instance so that tests can
monkeypatch environment variables before the app is constructed and
``get_settings()`` reads them at request time (not import time).

Routes:
  GET  /health              → {"status": "ok"}
  GET  /api/daily-shortlist → reads DATA_DIR/latest_shortlist.json
  GET  /api/track-record    → derives scorecard from DATA_DIR/calls.jsonl
  POST /api/run             → guarded by x-run-secret header
"""
from __future__ import annotations

import json
import pathlib
from datetime import datetime, timezone

from fastapi import BackgroundTasks, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from meridian.api.schemas import (
    DailyShortlistResponse,
    EvaluateRequest,
    EvaluateResponse,
    HealthResponse,
    RunResponse,
    TrackRecordResponse,
    TrackRecordSummary,
)
from meridian.trackrecord.store import load_calls, derive_scorecard


# ---------------------------------------------------------------------------
# Background job
# ---------------------------------------------------------------------------


def _run_live_pipeline() -> None:
    """Execute the real Swarms pipeline and write today's artifacts.

    Runs in a FastAPI background task so ``POST /api/run`` returns immediately
    (the live swarm is slow and credit-bearing). Imports are deferred and
    ``meridian.run.main`` is looked up at call time so tests can monkeypatch it.
    Any failure is logged, never raised — a bad run must not crash the web
    process or leave the request hanging.
    """
    import logging

    from meridian import run

    log = logging.getLogger("meridian.api")
    try:
        picks = run.main(["--live"])
        log.info("Live pipeline run wrote %d pick(s)", len(picks))
    except Exception:  # pragma: no cover - defensive, exercised in prod only
        log.exception("Live pipeline run failed")


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------


def create_app() -> FastAPI:
    """Create and return a configured FastAPI application instance.

    Settings (including DATA_DIR) are read **at request time** via
    ``get_settings()`` so pytest's ``monkeypatch.setenv`` takes effect before
    the first request without needing to restart the process.
    """
    app = FastAPI(title="Meridian Scout API", version="0.1.0")

    # Permissive CORS for dev — tighten via env later.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ------------------------------------------------------------------
    # GET /health
    # ------------------------------------------------------------------

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="ok")

    # ------------------------------------------------------------------
    # GET /api/daily-shortlist
    # ------------------------------------------------------------------

    @app.get("/api/daily-shortlist", response_model=DailyShortlistResponse)
    def daily_shortlist() -> DailyShortlistResponse:
        """Return the most-recently generated shortlist.

        If none has been saved yet, degrade gracefully: return 200 with
        ``picks: []`` and ``generated_at: null`` but keep all contract keys
        (disclaimer, data_source, …) so the frontend never sees a missing field.
        """
        from meridian.config import get_settings  # read at request time
        from meridian.trackrecord.store import load_shortlist

        settings = get_settings()
        raw = load_shortlist(settings.data_dir)

        if not raw:
            return DailyShortlistResponse()

        try:
            return DailyShortlistResponse(**raw)
        except Exception:
            # Corrupt / unexpected format — degrade gracefully
            return DailyShortlistResponse()

    # ------------------------------------------------------------------
    # GET /api/track-record
    # ------------------------------------------------------------------

    @app.get("/api/track-record", response_model=TrackRecordResponse)
    def track_record() -> TrackRecordResponse:
        """Build the public scorecard live from ``calls.jsonl``.

        Returns an empty scorecard (total_calls=0) when no calls have been
        logged yet.
        """
        from meridian.config import get_settings  # read at request time

        settings = get_settings()
        calls = load_calls(settings.data_dir)
        scorecard = derive_scorecard(calls)

        summary_data = scorecard["summary"]
        summary = TrackRecordSummary(
            total_calls=summary_data["total_calls"],
            hits=summary_data["hits"],
            misses=summary_data["misses"],
            open=summary_data["open"],
            hit_rate=summary_data["hit_rate"],
        )

        return TrackRecordResponse(
            updated_at=scorecard["updated_at"],
            summary=summary,
            calls=scorecard["calls"],
        )

    # ------------------------------------------------------------------
    # POST /api/run  (protected)
    # ------------------------------------------------------------------

    @app.post("/api/run", response_model=RunResponse)
    def run_pipeline(
        background_tasks: BackgroundTasks,
        x_run_secret: str = Header(default="", alias="x-run-secret"),
    ) -> RunResponse:
        """Trigger a real Swarms pipeline run.

        Guarded by the ``x-run-secret`` request header matching
        ``settings.run_secret``.  Returns 403 if the secret doesn't match or
        if ``run_secret`` is empty (no secret configured → deny all).

        On success the live swarm run is scheduled as a background task and the
        endpoint returns ``{"status": "queued"}`` immediately — the run writes
        ``latest_shortlist.json`` and appends to ``calls.jsonl`` when it finishes.
        """
        from meridian.config import get_settings  # read at request time

        settings = get_settings()

        # Deny if no secret is configured, or if the header doesn't match.
        if not settings.run_secret or x_run_secret != settings.run_secret:
            raise HTTPException(status_code=403, detail="Forbidden")

        background_tasks.add_task(_run_live_pipeline)
        return RunResponse(status="queued")

    # ------------------------------------------------------------------
    # POST /api/evaluate  (on-demand single-token scoring)
    # ------------------------------------------------------------------

    @app.post("/api/evaluate", response_model=EvaluateResponse)
    def evaluate(req: EvaluateRequest, live: bool = False) -> EvaluateResponse:
        """Score a single token on demand against the same rubric.

        Uses the deterministic MockScoutSwarm by default (instant, no credit);
        pass ``?live=1`` to use the real Swarms swarm. Risky tokens are scored
        and returned (with the risk flagged) rather than filtered out.
        """
        from meridian.config import get_settings
        from meridian.datafeed.dexscreener import fetch_token
        from meridian.datafeed.enrich import enrich_authorities
        from meridian.run import pick_to_response

        token = (req.token or "").strip()
        if not token:
            raise HTTPException(status_code=400, detail="token required")

        try:
            candidates = fetch_token(token)
        except Exception:
            candidates = []
        if not candidates:
            return EvaluateResponse(
                found=False, error="No Solana pair found for that token."
            )

        settings = get_settings()
        candidates = enrich_authorities(candidates, settings.solana_rpc_url)

        if live:
            from meridian.scouts.swarm import SwarmsScoutSwarm

            swarm = SwarmsScoutSwarm()
        else:
            from meridian.scouts.swarm import MockScoutSwarm

            swarm = MockScoutSwarm()

        try:
            picks = swarm.rank(candidates)
        except Exception:
            picks = []
        if not picks:
            return EvaluateResponse(found=False, error="Couldn't score that token.")

        return EvaluateResponse(found=True, pick=pick_to_response(picks[0]))

    return app
