"""Telegram bot — a thin client over the Meridian API.

Long-polls Telegram; for each command it fetches from the Meridian FastAPI
service and replies with a formatted message. No new dependencies (httpx only).

Commands:
  /start, /help  → intro + disclaimer
  /picks         → today's ranked shortlist
  /track         → the public track record (wins & misses)

Env:
  TELEGRAM_BOT_TOKEN  (required)  — from @BotFather
  MERIDIAN_API_URL    (default http://localhost:8000) — the FastAPI base URL

Run:  python -m meridian.bot
"""
from __future__ import annotations

import html
import os
import time
from collections.abc import Callable

import httpx

from meridian import config as _config  # noqa: F401 — import triggers load_dotenv()

API_URL = os.getenv("MERIDIAN_API_URL", "http://localhost:8000").rstrip("/")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TG = f"https://api.telegram.org/bot{TOKEN}"

DISCLAIMER = "Worth investigating — never financial advice."

START_TEXT = (
    "👋 <b>Meridian</b> — the discovery scout swarm for Solana.\n\n"
    "I scan new token launches, score each against a transparent rubric, and "
    "surface the few worth investigating today — with a public track record of "
    "every call.\n\n"
    "/picks — today's ranked shortlist\n"
    "/track — the public track record (wins &amp; misses)\n\n"
    f"<i>{DISCLAIMER}</i>"
)


def _esc(value: object) -> str:
    return html.escape(str(value))


def _fmt_score(score: object) -> str:
    return "—" if score is None else str(int(round(float(score))))


def format_picks(data: dict) -> str:
    """Render the daily-shortlist payload as an HTML Telegram message (pure)."""
    picks = data.get("picks") or []
    if not picks:
        return (
            "No shortlist yet today — the swarm hasn't posted a call. "
            "Check back soon."
        )
    when = data.get("as_of_date") or ""
    header = "🛰 <b>Today's shortlist</b>" + (f" · {_esc(when)}" if when else "")
    lines = [header, ""]
    for p in picks:
        tok = p.get("token", {})
        sym = tok.get("symbol", "?")
        rank = p.get("rank", "?")
        reasons = p.get("top_reasons") or []
        risk = p.get("standout_risk", "")
        read = p.get("one_line_read", "")
        lines.append(
            f"<b>#{_esc(rank)}  ${_esc(sym)}</b> — score "
            f"<b>{_fmt_score(p.get('composite_score'))}/100</b>"
        )
        if reasons:
            lines.append(f"  ✓ {_esc(reasons[0])}")
        if risk:
            lines.append(f"  ⚠ Risk: {_esc(risk)}")
        if read:
            lines.append(f"  <i>{_esc(read)}</i>")
        lines.append("")
    lines.append(f"<i>{DISCLAIMER}</i>")
    return "\n".join(lines).strip()


def format_track(data: dict) -> str:
    """Render the track-record payload as an HTML Telegram message (pure)."""
    summary = data.get("summary", {})
    total = summary.get("total_calls", 0)
    if not total:
        return (
            "Track record is empty so far — calls will appear here as the "
            "swarm makes them."
        )
    hit_rate = summary.get("hit_rate")
    hr_txt = "—" if hit_rate is None else f"{round(hit_rate * 100)}%"
    lines = [
        "📊 <b>Track record</b>",
        f"Calls: <b>{_esc(total)}</b> · Hits: <b>{_esc(summary.get('hits', 0))}</b> "
        f"· Misses: <b>{_esc(summary.get('misses', 0))}</b> "
        f"· Open: <b>{_esc(summary.get('open', 0))}</b>",
        f"Hit rate: <b>{hr_txt}</b>",
        "",
    ]
    for call in (data.get("calls") or [])[:8]:
        sym = call.get("token", {}).get("symbol", "?")
        status = call.get("status", "open")
        glyph = {"hit": "▲", "miss": "▼", "open": "•"}.get(status, "•")
        lines.append(
            f"{glyph} ${_esc(sym)} · scored {_fmt_score(call.get('score_at_call'))} "
            f"· {_esc(status)} · {_esc(call.get('date', ''))}"
        )
    lines.append("")
    lines.append("<i>Wins and misses both shown. Not financial advice.</i>")
    return "\n".join(lines).strip()


def _get(path: str) -> dict | None:
    try:
        resp = httpx.get(f"{API_URL}{path}", timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


def _send(chat_id: int, text: str) -> int | None:
    """Send a message; return its message_id (so it can be edited later)."""
    try:
        resp = httpx.post(
            f"{TG}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            },
            timeout=30,
        )
        return resp.json().get("result", {}).get("message_id")
    except Exception:
        return None


def _edit(chat_id: int, message_id: int, text: str) -> None:
    try:
        httpx.post(
            f"{TG}/editMessageText",
            json={
                "chat_id": chat_id,
                "message_id": message_id,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            },
            timeout=30,
        )
    except Exception:
        pass


def _reply(chat_id: int, ack: str, path: str, formatter: Callable[[dict], str]) -> None:
    """Send an instant ack, fetch from the API, then edit the ack into the
    result. The ack keeps the bot feeling responsive while the backend (which
    may be cold-starting) responds.
    """
    mid = _send(chat_id, ack)
    data = _get(path)
    text = (
        formatter(data)
        if data is not None
        else "Couldn't reach the swarm right now — it may be waking up. Try again in a moment."
    )
    if mid is not None:
        _edit(chat_id, mid, text)
    else:
        _send(chat_id, text)


def handle(text: str, chat_id: int) -> None:
    """Dispatch a single command to a reply."""
    cmd = text.strip().split()[0].lower().split("@")[0] if text.strip() else ""
    if cmd in ("/start", "/help"):
        _send(chat_id, START_TEXT)
    elif cmd == "/picks":
        _reply(chat_id, "🛰 Scanning today's launches…", "/api/daily-shortlist", format_picks)
    elif cmd == "/track":
        _reply(chat_id, "📊 Pulling the track record…", "/api/track-record", format_track)
    else:
        _send(chat_id, "Unknown command. Try /picks, /track, or /help.")


def main() -> None:
    if not TOKEN:
        raise SystemExit("TELEGRAM_BOT_TOKEN is not set (get one from @BotFather).")
    print(f"Meridian bot polling… (API: {API_URL})")
    offset: int | None = None
    with httpx.Client(timeout=40) as client:
        while True:
            try:
                params: dict[str, object] = {"timeout": 30}
                if offset is not None:
                    params["offset"] = offset
                resp = client.get(f"{TG}/getUpdates", params=params)
                updates = resp.json().get("result", [])
            except Exception:
                time.sleep(3)
                continue
            for update in updates:
                offset = update["update_id"] + 1
                msg = update.get("message") or update.get("channel_post")
                if not msg:
                    continue
                text = msg.get("text", "")
                chat_id = msg.get("chat", {}).get("id")
                if chat_id and text:
                    handle(text, chat_id)


if __name__ == "__main__":
    main()
