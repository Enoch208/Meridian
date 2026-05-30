"""Shared smart-money data shapes.

``WalletObservation`` = a single sighting of a wallet doing something
interesting (an early buy on a winner, a row in someone's top-traders feed,
a curated seed).  ``SmartMoneyWallet`` = an aggregated row in the watchlist.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class WalletObservation:
    address: str
    source: str  # "helius:earliest_buyers" | "birdeye:top_traders" | "curated"
    # Context — which token was this observed against
    token_mint: Optional[str] = None
    token_symbol: Optional[str] = None
    # Behavioural signals (where the source provides them)
    buy_timestamp: Optional[int] = None  # unix seconds
    pnl_usd: Optional[float] = None
    volume_usd: Optional[float] = None
    trade_count: Optional[int] = None
    # Where the wallet ranked in the source's per-token leaderboard.
    # For Helius "earliest_buyers", rank=1 means literally the first buyer.
    rank: Optional[int] = None
    notes: str = ""


@dataclass
class SmartMoneyWallet:
    """One row in the watchlist — the persisted, scored view of a wallet."""
    address: str
    score: float                              # 0-100 quality score
    label: Optional[str] = None               # human label (curated only)
    first_seen: str = ""                      # ISO datetime
    last_seen: str = ""                       # ISO datetime
    sources: list[str] = field(default_factory=list)  # which sources flagged this
    winners_caught: int = 0                   # distinct winning tokens this wallet was early on
    avg_entry_rank: Optional[float] = None    # avg rank across those tokens (lower = earlier)
    cumulative_pnl_usd: Optional[float] = None
    is_curated: bool = False
    notes: str = ""
