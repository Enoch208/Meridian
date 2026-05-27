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


class ScoreBreakdown(BaseModel):
    onchain: Optional[int] = None
    liquidity: Optional[int] = None
    momentum: Optional[int] = None
    smart_money: Optional[int] = None


class TokenMetrics(BaseModel):
    liquidity_usd: Optional[float] = None
    fdv: Optional[float] = None
    age_hours: Optional[float] = None
    volume_h24: Optional[float] = None
    buy_sell_ratio_h1: Optional[float] = None
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
# /api/evaluate  (on-demand single-token scoring)
# ---------------------------------------------------------------------------


class EvaluateRequest(BaseModel):
    token: str


class EvaluateResponse(BaseModel):
    found: bool
    pick: Optional[PickResponse] = None
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
