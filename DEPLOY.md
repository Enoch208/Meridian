# Deployment Guide

Meridian is split into a **Python FastAPI backend** (deployed on Render via Docker) and a **Next.js frontend** (deployed on Vercel). The two services communicate over HTTP; the only coupling is `NEXT_PUBLIC_MERIDIAN_API_URL`.

---

## 1. Deploy the backend to Render

### Prerequisites

- A [Render](https://render.com) account linked to this GitHub repo.
- A **Swarms API key** from <https://swarms.world/platform/api-keys> (Frenzy Mode = zero-cost).
- A strong random string for `MERIDIAN_RUN_SECRET` (e.g. `openssl rand -hex 32`).

### Steps

1. **Create a new Web Service** in the Render dashboard:
   - Choose **"Deploy from a GitHub repo"** → select this repo.
   - Set **Environment** to `Docker`.
   - Set **Dockerfile Path** to `./backend/Dockerfile`.
   - Set **Docker Context** to `./backend` (or repo root — the Dockerfile only copies `pyproject.toml` and `meridian/`).

2. **Set secret environment variables** (Render dashboard → Environment → Add):

   | Key | Value |
   |---|---|
   | `SWARMS_API_KEY` | `sk-…` (your Swarms key) |
   | `MERIDIAN_RUN_SECRET` | random secret string |

   The non-secret defaults (`SOLANA_RPC_URL`, `MERIDIAN_MODEL`, `DATA_DIR`) are already set in `backend/render.yaml` and will be applied automatically if you use the Blueprint flow.

3. **Persistent disk (strongly recommended):**
   The track record (`calls.jsonl`) lives in `DATA_DIR` (`/data` by default). On Render's free tier the filesystem is **ephemeral** — every deploy or restart wipes it and the public track record resets to zero. To preserve history:
   - Upgrade to a paid plan and attach a **Disk** at `/data` (uncomment the `disk:` block in `backend/render.yaml`).
   - Alternatively, point `DATA_DIR` to `/tmp` (ephemeral, but at least explicit) while you're still doing demo runs.

4. **Seed initial data** by triggering a pipeline run. SSH into the service shell (Render dashboard → Shell) or trigger via the API:

   ```bash
   # Inside the Render shell (installs are already done):
   python -m meridian.run --live          # real Swarms swarm + live DexScreener data
   ```

   Or trigger remotely once the service is up:

   ```bash
   curl -X POST https://<your-render-service>.onrender.com/api/run \
        -H "x-run-secret: <MERIDIAN_RUN_SECRET>"
   ```

5. **Verify** the backend is live:

   ```bash
   curl https://<your-render-service>.onrender.com/health
   # → {"status":"ok"}
   ```

   Note the service URL — you will need it for the frontend step.

---

## 2. Deploy the frontend to Vercel

1. Import the repo into [Vercel](https://vercel.com).
2. Set **Root Directory** to `frontend`.
3. Add the environment variable:

   | Key | Value |
   |---|---|
   | `NEXT_PUBLIC_MERIDIAN_API_URL` | `https://<your-render-service>.onrender.com` |

4. Deploy. Vercel auto-detects Next.js; no further configuration is needed.

---

## 3. CORS

The backend already allows all origins (`allow_origins=["*"]` in `backend/meridian/api/server.py`), so the Vercel frontend can reach the Render backend without any additional CORS configuration.

---

## 4. Important notes for judges / demo use

- **Track record honesty:** `calls.jsonl` is append-only. Once a real run is logged, misses are never silently dropped. Clear `data/` (or provision a fresh disk) before going public so the scorecard only reflects real calls.
- **Ephemeral filesystem warning:** Without a persistent disk, every Render deploy resets the shortlist and track record. The service remains functional but starts from zero.
- **Rate limits:** The public Solana RPC (`api.mainnet-beta.solana.com`) can throttle under load. Replace with a private endpoint (Helius, QuickNode, etc.) for production traffic.
- **Model availability:** `MERIDIAN_MODEL` must be a model listed in `GET https://api.swarms.world/v1/models/available`. The default `gpt-4o-mini` is reliably available.
