"""Pydantic v2 response models — the frontend contract (spec §7).

These models are the definitive serialization shape served to the frontend.
Every field that spec §7 names is present; optional fields use ``None`` as the
empty/unknown sentinel so the JSON contract is stable.
"""
from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Shared sub-models
# ---------------------------------------------------------------------------


class TokenInfo(BaseModel):
    name: str
    symbol: str
    address: str
    pair_url: Optional[str] = None
    image_url: Optional[str] = None
    website: Optional[str] = None
    twitter: Optional[str] = None
    telegram: Optional[str] = None


class ScoreBreakdown(BaseModel):
    onchain: Optional[int] = None
    liquidity: Optional[int] = None
    momentum: Optional[int] = None
    smart_money: Optional[int] = None


class TokenMetrics(BaseModel):
    liquidity_usd: Optional[float] = None
    fdv: Optional[float] = None
    market_cap: Optional[float] = None
    age_hours: Optional[float] = None
    volume_h24: Optional[float] = None
    buy_sell_ratio_h1: Optional[float] = None
    buys_h1: Optional[int] = None
    sells_h1: Optional[int] = None
    holder_count: Optional[int] = None
    top_holders_pct: Optional[float] = None
    dev_holding_pct: Optional[float] = None
    organic_score: Optional[str] = None
    dev_wallet: Optional[str] = None
    price_usd: Optional[float] = None
    price_change_24h: Optional[float] = None
    launchpad: Optional[str] = None
    mint_authority: Optional[str] = None
    freeze_authority: Optional[str] = None


# ---------------------------------------------------------------------------
# /api/daily-shortlist
# ---------------------------------------------------------------------------


class PickResponse(BaseModel):
    rank: int
    token: TokenInfo
    composite_score: int
    scores: dict[str, Optional[int]]
    top_reasons: list[str]
    standout_risk: str
    one_line_read: str
    metrics: Optional[TokenMetrics] = None
    unknowns: list[str] = []


class DailyShortlistResponse(BaseModel):
    generated_at: Optional[str] = None
    as_of_date: Optional[str] = None
    data_source: str = "dexscreener+solana-rpc"
    disclaimer: str = (
        "Not financial advice. "
        "Every pick is 'worth investigating', never 'buy'."
    )
    free_tier_cutoff: int = 1
    picks: list[PickResponse] = []


# ---------------------------------------------------------------------------
# /api/track-record
# ---------------------------------------------------------------------------


class TrackRecordSummary(BaseModel):
    total_calls: int
    hits: int
    misses: int
    open: int
    hit_rate: Optional[float] = None


class CallRecord(BaseModel):
    date: str
    rank: int
    token: TokenInfo
    score_at_call: int
    price_at_call_usd: Optional[float] = None
    price_now_usd: Optional[float] = None
    pct_change: Optional[float] = None
    status: str


class TrackRecordResponse(BaseModel):
    updated_at: str
    summary: TrackRecordSummary
    calls: list[CallRecord] = []


# ---------------------------------------------------------------------------
# /api/smart-money/watchlist
# ---------------------------------------------------------------------------


class WatchlistWallet(BaseModel):
    address: str
    score: float
    label: Optional[str] = None
    sources: list[str] = []
    winners_caught: int = 0
    avg_entry_rank: Optional[float] = None
    cumulative_pnl_usd: Optional[float] = None
    is_curated: bool = False
    first_seen: str = ""
    last_seen: str = ""


class WatchlistResponse(BaseModel):
    updated_at: Optional[str] = None
    count: int = 0
    wallets: list[WatchlistWallet] = []


# ---------------------------------------------------------------------------
# /api/evaluate  (on-demand single-token scoring)
# ---------------------------------------------------------------------------


class EvaluateRequest(BaseModel):
    token: str


class SecurityCheck(BaseModel):
    """Optional third-party honeypot / contract security signals."""
    overall_score: Optional[int] = None
    is_honeypot: Optional[bool] = None
    honeypot_reason: Optional[str] = None
    buy_tax: Optional[float] = None
    sell_tax: Optional[float] = None
    transfer_tax: Optional[float] = None
    code_score: Optional[int] = None
    market_score: Optional[int] = None
    liquidity_locked_pct: Optional[float] = None


class EvaluateResponse(BaseModel):
    found: bool
    pick: Optional[PickResponse] = None
    security: Optional[SecurityCheck] = None
    disclaimer: str = (
        "Not financial advice. 'Worth investigating', never 'buy'."
    )
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# /api/run
# ---------------------------------------------------------------------------


class RunResponse(BaseModel):
    status: str


# ---------------------------------------------------------------------------
# /health
# ---------------------------------------------------------------------------


class HealthResponse(BaseModel):
    status: str
