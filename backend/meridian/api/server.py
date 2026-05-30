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
    SecurityCheck,
    RunResponse,
    TrackRecordResponse,
    TrackRecordSummary,
    WatchlistResponse,
    WatchlistWallet,
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


def _run_smart_money_refresh() -> None:
    """Recompute the smart-money watchlist on the server.

    Same shape as ``_run_live_pipeline`` — background task, deferred imports,
    swallows exceptions into the logger. Writes to MongoDB when MONGODB_URI is
    configured (the Render path); otherwise to ``<DATA_DIR>/smart_money_wallets.json``.
    Reads HELIUS_API_KEY and BIRDEYE_API_KEY from the process env (set those
    in Render's dashboard).
    """
    import logging

    from meridian.datafeed.smart_money import refresh as sm_refresh

    log = logging.getLogger("meridian.api")
    try:
        wallets = sm_refresh.run_refresh()
        log.info("smart-money refresh wrote %d wallet(s)", len(wallets))
    except Exception:  # pragma: no cover - defensive
        log.exception("smart-money refresh failed")


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------


def create_app() -> FastAPI:
    """Create and return a configured FastAPI application instance.

    Settings (including DATA_DIR) are read **at request time** via
    ``get_settings()`` so pytest's ``monkeypatch.setenv`` takes effect before
    the first request without needing to restart the process.
    """
    app = FastAPI(
        title="Meridian Scout API",
        version="0.1.0",
        description=(
            "The discovery scout swarm for Solana launches. "
            "Three public read endpoints (daily shortlist, track record, "
            "evaluate any token) and one admin endpoint to trigger a run. "
            "Every pick is framed as 'worth investigating' — never financial advice."
        ),
        servers=[
            {
                "url": "https://meridian-backend-qae0.onrender.com",
                "description": "Production",
            }
        ],
    )

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

    @app.get(
        "/health",
        response_model=HealthResponse,
        tags=["Health"],
        summary="Heartbeat",
    )
    def health() -> HealthResponse:
        return HealthResponse(status="ok")

    # ------------------------------------------------------------------
    # GET /api/daily-shortlist
    # ------------------------------------------------------------------

    @app.get(
        "/api/daily-shortlist",
        response_model=DailyShortlistResponse,
        tags=["Public"],
        summary="Today's ranked shortlist",
    )
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

    @app.get(
        "/api/track-record",
        response_model=TrackRecordResponse,
        tags=["Public"],
        summary="Public track record (hits / misses / open)",
    )
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

    @app.post(
        "/api/run",
        response_model=RunResponse,
        tags=["Admin"],
        summary="Trigger a new daily run (gated by x-run-secret)",
    )
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
    # POST /api/smart-money/refresh  (protected)
    # ------------------------------------------------------------------

    @app.post(
        "/api/smart-money/refresh",
        response_model=RunResponse,
        tags=["Admin"],
        summary="Recompute the smart-money watchlist (gated by x-run-secret)",
    )
    def smart_money_refresh(
        background_tasks: BackgroundTasks,
        x_run_secret: str = Header(default="", alias="x-run-secret"),
    ) -> RunResponse:
        """Trigger a fresh smart-money discovery pass.

        Queries the configured sources (Helius + Birdeye when their keys are
        set in the server env), aggregates wallets that appear across multiple
        recent winners, and upserts them into the watchlist (MongoDB if
        ``MONGODB_URI`` is configured, otherwise a local JSON file).
        Same auth + 403 semantics as ``POST /api/run`` — guarded by
        ``x-run-secret``. Returns ``{"status": "queued"}`` immediately and
        finishes the work in a background task (the swarm of API calls takes
        ~20–60s).
        """
        from meridian.config import get_settings

        settings = get_settings()
        if not settings.run_secret or x_run_secret != settings.run_secret:
            raise HTTPException(status_code=403, detail="Forbidden")

        background_tasks.add_task(_run_smart_money_refresh)
        return RunResponse(status="queued")

    # ------------------------------------------------------------------
    # GET /api/smart-money/watchlist
    # ------------------------------------------------------------------

    @app.get(
        "/api/smart-money/watchlist",
        response_model=WatchlistResponse,
        tags=["Public"],
        summary="The current smart-money watchlist",
    )
    def smart_money_watchlist(limit: int = 50, min_score: float = 0) -> WatchlistResponse:
        """Read the smart-money wallet watchlist (no auth required).

        Reads from MongoDB when ``MONGODB_URI`` is configured, otherwise from
        the local JSON file. Returns an empty list (200, ``count: 0``) when
        the discovery pass has not run yet — never errors.
        """
        from meridian.config import get_settings
        from meridian.datafeed.smart_money.watchlist import load_watchlist

        settings = get_settings()
        try:
            wallets = load_watchlist(settings.data_dir)
        except Exception:
            wallets = []
        filtered = [w for w in wallets if w.score >= min_score][: max(1, min(limit, 200))]
        return WatchlistResponse(
            updated_at=filtered[0].last_seen if filtered else None,
            count=len(filtered),
            wallets=[
                WatchlistWallet(
                    address=w.address,
                    score=w.score,
                    label=w.label,
                    sources=w.sources,
                    winners_caught=w.winners_caught,
                    avg_entry_rank=w.avg_entry_rank,
                    cumulative_pnl_usd=w.cumulative_pnl_usd,
                    is_curated=w.is_curated,
                    first_seen=w.first_seen,
                    last_seen=w.last_seen,
                )
                for w in filtered
            ],
        )

    # ------------------------------------------------------------------
    # POST /api/evaluate  (on-demand single-token scoring)
    # ------------------------------------------------------------------

    @app.post(
        "/api/evaluate",
        response_model=EvaluateResponse,
        tags=["Public"],
        summary="Score any Solana token on demand",
    )
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

        # Enrich with Jupiter market data: fill liquidity/price when DexScreener
        # lacked them (bonding-curve tokens), and always add 24h change +
        # launchpad. Purely additive — None on failure.
        import dataclasses

        from meridian.datafeed.jupiter import fetch_market

        cand = candidates[0]
        mkt = fetch_market(cand.address)
        if mkt:
            candidates[0] = dataclasses.replace(
                cand,
                liquidity_usd=cand.liquidity_usd
                if cand.liquidity_usd is not None
                else mkt.get("liquidity_usd"),
                price_usd=cand.price_usd
                if cand.price_usd is not None
                else mkt.get("usd_price"),
                fdv=cand.fdv if cand.fdv is not None else mkt.get("fdv"),
                market_cap=cand.market_cap
                if cand.market_cap is not None
                else mkt.get("market_cap"),
                price_change_24h=mkt.get("price_change_24h"),
                launchpad=mkt.get("launchpad"),
                image_url=cand.image_url
                if cand.image_url is not None
                else mkt.get("icon"),
                holder_count=mkt.get("holder_count"),
                top_holders_pct=mkt.get("top_holders_pct"),
                organic_score=mkt.get("organic_score"),
                dev_wallet=mkt.get("dev_wallet"),
                # Prefer Jupiter's tx counts (it reads the bonding curve
                # directly; DexScreener's 1h often lags on new tokens), but use
                # `is not None` so a real 0 is preserved — never conflated with
                # missing data.
                buys_h1=mkt.get("buys_1h")
                if mkt.get("buys_1h") is not None
                else cand.buys_h1,
                sells_h1=mkt.get("sells_1h")
                if mkt.get("sells_1h") is not None
                else cand.sells_h1,
            )

        # Dev wallet holding %: dev balance / total supply (one RPC call).
        cand = candidates[0]
        supply = mkt.get("total_supply") if mkt else None
        if cand.dev_wallet and supply and supply > 0:
            from meridian.datafeed.solana_rpc import fetch_owner_token_balance

            bal = fetch_owner_token_balance(
                cand.dev_wallet, cand.address, settings.solana_rpc_url
            )
            if bal is not None:
                candidates[0] = dataclasses.replace(
                    cand, dev_holding_pct=round(bal / supply * 100, 2)
                )

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

        # Optional security/honeypot enrichment (server-side, env-gated). Any
        # failure → None, so the response is identical to before when disabled.
        from meridian.datafeed.tokencheck import fetch_security

        sec = fetch_security(candidates[0].address)
        security = SecurityCheck(**sec) if sec else None

        return EvaluateResponse(
            found=True, pick=pick_to_response(picks[0]), security=security
        )

    return app
