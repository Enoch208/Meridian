# Meridian Backend

A discovery scout swarm for Solana. Pulls recent token launches (DexScreener +
one Solana RPC call), scores them with a **real Swarms multi-agent swarm**
(3 scouts → synthesizing lead, via the Swarms cloud API — zero-cost under
Frenzy Mode), and serves a ranked daily shortlist + an honest, append-only
track record over FastAPI.

## Setup

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
cp .env.example .env     # then fill in SWARMS_API_KEY
```

`.env` and `data/` are gitignored. No model-provider key (OpenAI etc.) is
needed — the swarm runs on Swarms infra via `SWARMS_API_KEY`.

## Generate today's shortlist

```bash
.venv/bin/python -m meridian.run            # mock swarm + live DexScreener data
.venv/bin/python -m meridian.run --live     # REAL Swarms swarm (uses SWARMS_API_KEY)
.venv/bin/python -m meridian.run --demo     # synthetic candidates, no network (for the frontend)
.venv/bin/python -m meridian.run --live --demo   # real swarm on synthetic data (offline-ish smoke)
```

Each run writes `data/latest_shortlist.json` and appends to the immutable
`data/calls.jsonl`. **Before going live, clear `data/` of demo/test calls** so
the public track record only contains real calls.

## Run the API

```bash
.venv/bin/uvicorn meridian.api.server:create_app --factory --port 8000
```

Endpoints (the frontend contract — see spec §7):

| Method | Path | Returns |
|---|---|---|
| GET | `/health` | `{"status":"ok"}` |
| GET | `/api/daily-shortlist` | latest ranked picks (degrades to `picks:[]` if none yet) |
| GET | `/api/track-record` | derived public scorecard from `calls.jsonl` |
| POST | `/api/run` | triggers a re-run; guarded by `x-run-secret` header |

## Frontend integration

Set in the Next.js app: `NEXT_PUBLIC_MERIDIAN_API_URL=http://localhost:8000`.
The two GET endpoints above are the only ones the frontend needs.

## Tests

```bash
.venv/bin/pytest                       # full suite (mock swarm, no credit spent)
RUN_LIVE_SWARM=1 .venv/bin/pytest -k live   # opt-in real-swarm smoke test
```

## Architecture (one screen)

```
datafeed/  dexscreener.py + solana_rpc.py + enrich.py  → Candidate (Unknown-aware)
scoring/   prefilter.py                                 → drop obvious traps deterministically
scouts/    prompts.py (honesty rules) + swarm.py        → SwarmsScoutSwarm (cloud API) | MockScoutSwarm
pipeline.py  fetch → enrich → prefilter → swarm.rank    → list[Pick]
trackrecord/ store.py (append-only calls.jsonl) + update.py (hit/miss)
api/       schemas.py (contract) + server.py (FastAPI)
run.py     CLI entrypoint
```

The swarm runs in the pipeline (slow/credit) and writes artifacts; FastAPI only
reads them, so HTTP stays fast. The `calls.jsonl` log is append-only and is the
source of truth — the scorecard is derived from it, so misses are never silently
dropped (the track record is the product's moat; it must stay honest).

## Deploy

See [DEPLOY.md](../DEPLOY.md) at the repo root for step-by-step instructions to
deploy the backend to Render (Docker) and the frontend to Vercel.
