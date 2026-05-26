"""Shared data models — the contract every component imports.

`None` on a numeric metric means the data source did not provide it; it is
surfaced to agents as the explicit ``UNKNOWN`` sentinel so they can down-weight
it rather than invent a value.
"""
from dataclasses import dataclass, field
from typing import Optional

UNKNOWN = "Unknown"  # explicit sentinel; never guess a missing signal


@dataclass
class Candidate:
    address: str  # token mint
    name: str
    symbol: str
    pair_url: str
    # numeric metrics — None means the source didn't provide it (-> Unknown to agents)
    liquidity_usd: Optional[float] = None
    fdv: Optional[float] = None
    market_cap: Optional[float] = None
    age_hours: Optional[float] = None
    volume_h24: Optional[float] = None
    volume_h6: Optional[float] = None
    volume_h1: Optional[float] = None
    buys_h1: Optional[int] = None
    sells_h1: Optional[int] = None
    price_usd: Optional[float] = None
    # on-chain (from RPC); strings: "renounced" | "live:<pubkey>" | UNKNOWN
    mint_authority: str = UNKNOWN
    freeze_authority: str = UNKNOWN

    def buy_sell_ratio_h1(self) -> Optional[float]:
        if self.buys_h1 is None or self.sells_h1 is None:
            return None
        return self.buys_h1 / max(self.sells_h1, 1)

    def liq_to_fdv(self) -> Optional[float]:
        if self.liquidity_usd is None or not self.fdv:
            return None
        return self.liquidity_usd / self.fdv


@dataclass
class ScoutResult:
    scout: str  # "onchain" | "liquidity" | "momentum"
    score: Optional[int]  # 0-100, None = Unknown
    flags: list[str] = field(default_factory=list)
    rationale: str = ""


@dataclass
class Pick:
    rank: int
    candidate: Candidate
    composite_score: int
    scores: dict  # {"onchain":70,"liquidity":85,"momentum":80,"smart_money":None}
    top_reasons: list[str]
    standout_risk: str
    one_line_read: str
    unknowns: list[str]
