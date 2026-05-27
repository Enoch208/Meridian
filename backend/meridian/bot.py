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
import logging
import os
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor

import httpx

from meridian import config as _config  # noqa: F401 — import triggers load_dotenv()

API_URL = os.getenv("MERIDIAN_API_URL", "http://localhost:8000").rstrip("/")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TG = f"https://api.telegram.org/bot{TOKEN}"
POLL_TIMEOUT = max(1, int(os.getenv("TELEGRAM_POLL_TIMEOUT", "2")))
LOG = logging.getLogger("meridian.bot")
_HTTP_CLIENT: httpx.Client | None = None

DISCLAIMER = "Worth investigating — never financial advice."

START_TEXT = (
    "👋 <b>Meridian</b> — the discovery scout swarm for Solana.\n\n"
    "I scan new token launches, score each against a transparent rubric, and "
    "surface the few worth investigating today — with a public track record of "
    "every call.\n\n"
    "/picks — today's ranked shortlist\n"
    "/track — the public track record (wins &amp; misses)\n"
    "/check &lt;address&gt; — score any Solana token\n\n"
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
    started = time.perf_counter()
    try:
        resp = (
            _HTTP_CLIENT.get(f"{API_URL}{path}", timeout=30)
            if _HTTP_CLIENT
            else httpx.get(f"{API_URL}{path}", timeout=30)
        )
        resp.raise_for_status()
        LOG.info("api GET %s completed in %.3fs", path, time.perf_counter() - started)
        return resp.json()
    except Exception as exc:
        LOG.warning(
            "api GET %s failed after %.3fs: %s",
            path,
            time.perf_counter() - started,
            exc,
        )
        return None


def _post(path: str, payload: dict) -> dict | None:
    started = time.perf_counter()
    try:
        resp = (
            _HTTP_CLIENT.post(f"{API_URL}{path}", json=payload, timeout=70)
            if _HTTP_CLIENT
            else httpx.post(f"{API_URL}{path}", json=payload, timeout=70)
        )
        resp.raise_for_status()
        LOG.info("api POST %s completed in %.3fs", path, time.perf_counter() - started)
        return resp.json()
    except Exception as exc:
        LOG.warning(
            "api POST %s failed after %.3fs: %s",
            path,
            time.perf_counter() - started,
            exc,
        )
        return None


def format_evaluate(data: dict | None) -> str:
    """Render an /api/evaluate response as an HTML Telegram message (pure)."""
    if not data or not data.get("found") or not data.get("pick"):
        if data and data.get("error"):
            return _esc(data["error"])
        return "No Solana pair found for that token."
    p = data["pick"]
    tok = p.get("token", {})
    scores = p.get("scores", {})
    lines = [
        f"🔎 <b>${_esc(tok.get('symbol', '?'))}</b> — score "
        f"<b>{_fmt_score(p.get('composite_score'))}/100</b>",
        f"<i>{_esc(tok.get('name', ''))}</i>",
        "",
        f"On-chain {_fmt_score(scores.get('onchain'))} · "
        f"Liquidity {_fmt_score(scores.get('liquidity'))} · "
        f"Momentum {_fmt_score(scores.get('momentum'))} · "
        f"Smart-money {_fmt_score(scores.get('smart_money'))}",
        "",
    ]
    m = p.get("metrics") or {}
    mbits = []
    if m.get("liquidity_usd") is not None:
        mbits.append(f"💧 ${m['liquidity_usd']:,.0f} liq")
    if m.get("holder_count") is not None:
        mbits.append(f"👥 {m['holder_count']:,} holders")
    if m.get("price_change_24h") is not None:
        mbits.append(f"24h {m['price_change_24h']:+.0f}%")
    if mbits:
        lines.append(_esc(" · ".join(mbits)))
        lines.append("")

    for reason in (p.get("top_reasons") or [])[:2]:
        lines.append(f"✓ {_esc(reason)}")
    if p.get("standout_risk"):
        lines.append(f"⚠ Risk: {_esc(p['standout_risk'])}")
    if p.get("one_line_read"):
        lines.append(f"<i>{_esc(p['one_line_read'])}</i>")

    sec = data.get("security")
    if sec:
        bits = []
        hp = sec.get("is_honeypot")
        if hp is True:
            bits.append("⛔ HONEYPOT")
        elif hp is False:
            bits.append("✅ not a honeypot")
        bt, st = sec.get("buy_tax"), sec.get("sell_tax")
        if bt is not None or st is not None:
            bt_s = bt if bt is not None else "—"
            st_s = st if st is not None else "—"
            bits.append(f"tax {bt_s}/{st_s}%")
        if sec.get("overall_score") is not None:
            bits.append(f"safety {sec['overall_score']}/100")
        if bits:
            lines.append(f"🛡 {' · '.join(_esc(b) for b in bits)}")

    lines.append("")
    lines.append(f"<i>{DISCLAIMER}</i>")
    return "\n".join(lines).strip()


def _send(chat_id: int, text: str) -> int | None:
    """Send a message; return its message_id (so it can be edited later)."""
    started = time.perf_counter()
    try:
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
        resp = (
            _HTTP_CLIENT.post(f"{TG}/sendMessage", json=payload, timeout=30)
            if _HTTP_CLIENT
            else httpx.post(f"{TG}/sendMessage", json=payload, timeout=30)
        )
        resp.raise_for_status()
        LOG.info("telegram sendMessage completed in %.3fs", time.perf_counter() - started)
        return resp.json().get("result", {}).get("message_id")
    except Exception as exc:
        LOG.warning(
            "telegram sendMessage failed after %.3fs: %s",
            time.perf_counter() - started,
            exc,
        )
        return None


def _edit(chat_id: int, message_id: int, text: str) -> None:
    started = time.perf_counter()
    try:
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
        resp = (
            _HTTP_CLIENT.post(f"{TG}/editMessageText", json=payload, timeout=30)
            if _HTTP_CLIENT
            else httpx.post(f"{TG}/editMessageText", json=payload, timeout=30)
        )
        resp.raise_for_status()
        LOG.info(
            "telegram editMessageText completed in %.3fs", time.perf_counter() - started
        )
    except Exception as exc:
        LOG.warning(
            "telegram editMessageText failed after %.3fs: %s",
            time.perf_counter() - started,
            exc,
        )


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
    started = time.perf_counter()
    try:
        if cmd in ("/start", "/help"):
            _send(chat_id, START_TEXT)
        elif cmd == "/picks":
            _reply(chat_id, "🛰 Scanning today's launches…", "/api/daily-shortlist", format_picks)
        elif cmd == "/track":
            _reply(chat_id, "📊 Pulling the track record…", "/api/track-record", format_track)
        elif cmd == "/check":
            parts = text.strip().split(maxsplit=1)
            if len(parts) < 2 or not parts[1].strip():
                _send(chat_id, "Usage: <code>/check &lt;token address&gt;</code>")
            else:
                mid = _send(chat_id, "🔎 Evaluating…")
                data = _post("/api/evaluate", {"token": parts[1].strip()})
                out = format_evaluate(data)
                if mid is not None:
                    _edit(chat_id, mid, out)
                else:
                    _send(chat_id, out)
        else:
            _send(chat_id, "Unknown command. Try /picks, /track, /check, or /help.")
    finally:
        LOG.info("command %s completed in %.3fs", cmd or "<empty>", time.perf_counter() - started)


def main() -> None:
    global _HTTP_CLIENT

    if not TOKEN:
        raise SystemExit("TELEGRAM_BOT_TOKEN is not set (get one from @BotFather).")
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    # httpx logs include the Telegram token because it is embedded in the URL.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    print(f"Meridian bot polling... (API: {API_URL}, poll timeout: {POLL_TIMEOUT}s)")
    offset: int | None = None
    with httpx.Client(timeout=40) as client, ThreadPoolExecutor(
        max_workers=8, thread_name_prefix="telegram-command"
    ) as executor:
        _HTTP_CLIENT = client
        while True:
            try:
                params: dict[str, object] = {"timeout": POLL_TIMEOUT}
                if offset is not None:
                    params["offset"] = offset
                resp = client.get(f"{TG}/getUpdates", params=params)
                resp.raise_for_status()
                updates = resp.json().get("result", [])
            except Exception as exc:
                LOG.warning("telegram getUpdates failed: %s", exc)
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
                    cmd = text.strip().split()[0].lower().split("@")[0]
                    received_at = msg.get("date")
                    if isinstance(received_at, int):
                        LOG.info(
                            "received %s after %.3fs in telegram queue",
                            cmd,
                            max(0.0, time.time() - received_at),
                        )
                    else:
                        LOG.info("received %s", cmd)
                    executor.submit(handle, text, chat_id)


if __name__ == "__main__":
    main()
