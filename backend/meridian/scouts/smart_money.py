"""Smart-money scout.

Given a candidate token, score how much of Meridian's curated/discovered
smart-money watchlist showed up as early buyers of that mint. Honest by
construction: missing watchlist or missing chain data → ``None`` + ``unknowns``
entry, never an invented number.

Algorithm:
  1. Pull the first ~100 distinct buyers of the candidate's mint via Helius
     (same query the discovery pipeline uses to *find* smart-money — we just
     intersect against the watchlist this time).
  2. Intersect with watchlist addresses.
  3. Score blends **breadth** (how many distinct watchlist wallets) with
     **quality** (average watchlist score of the hits). No hits = honest 25.
"""
from __future__ import annotations

import logging
from typing import Callable, Optional

import httpx

from meridian.datafeed.models import Candidate
from meridian.datafeed.smart_money import helius
from meridian.datafeed.smart_money.models import SmartMoneyWallet

log = logging.getLogger(__name__)

# Public type: a scorer takes a candidate, returns (score, reasons, unknowns).
# ``score`` is 0-100 or ``None`` (Unknown — excluded from composite, surfaced
# in ``unknowns``). Reasons are short bullets that flow into the Pick's
# ``top_reasons``.
ScoreResult = tuple[Optional[int], list[str], list[str]]
SmartMoneyScorer = Callable[[Candidate], ScoreResult]


def score_candidate(
    candidate: Candidate,
    watchlist: list[SmartMoneyWallet],
    *,
    helius_key: Optional[str],
    helius_limit: int = 100,
    client: Optional[httpx.Client] = None,
) -> ScoreResult:
    """Deterministically score one candidate against the watchlist.

    Returns ``(score, reasons, unknowns)``. ``unknowns`` carries
    ``"smart_money"`` when we can't produce a score; the caller is expected to
    propagate it into the Pick's ``unknowns`` list.
    """
    if not watchlist:
        return None, [], ["smart_money"]
    if not helius_key:
        return None, [], ["smart_money"]
    if not candidate.address:
        return None, [], ["smart_money"]

    by_addr = {w.address: w for w in watchlist}

    buyers = helius.fetch_earliest_buyers(
        candidate.address, api_key=helius_key, limit=helius_limit, client=client,
    )
    if not buyers:
        log.debug("smart_money: no Helius buyers for %s", candidate.address[:10])
        return None, [], ["smart_money"]

    hits: list[tuple[int, SmartMoneyWallet]] = []
    for buyer in buyers:
        sm = by_addr.get(buyer.address)
        if sm and buyer.rank is not None:
            hits.append((buyer.rank, sm))

    if not hits:
        # Real signal: chain data is here, watchlist is here, no overlap.
        # That's a low-but-not-null score — smart-money has *not* shown up.
        return 25, [], []

    n_hits = len(hits)
    avg_quality = sum(w.score for _, w in hits) / n_hits

    # Breadth: each hit adds 15, capped at 75 (5+ hits saturates breadth).
    breadth = min(75.0, n_hits * 15.0)
    # Quality: average wallet score nudges the breadth up by up to +25.
    quality_bonus = (avg_quality / 100.0) * 25.0

    score = int(round(min(100.0, breadth + quality_bonus)))

    reasons: list[str] = []
    if n_hits >= 3:
        reasons.append(f"{n_hits} smart-money wallets bought early")
    else:
        labels = [
            (w.label or f"score {w.score:.0f}").strip()
            for _, w in sorted(hits, key=lambda h: h[1].score, reverse=True)[:2]
        ]
        reasons.append("Smart-money interest: " + ", ".join(labels))

    return score, reasons, []


def make_scorer(
    watchlist: list[SmartMoneyWallet],
    *,
    helius_key: Optional[str],
    helius_limit: int = 100,
    client: Optional[httpx.Client] = None,
) -> SmartMoneyScorer:
    """Bind watchlist + key so callers see a clean ``(Candidate) -> ScoreResult``."""

    def scorer(c: Candidate) -> ScoreResult:
        return score_candidate(
            c, watchlist,
            helius_key=helius_key,
            helius_limit=helius_limit,
            client=client,
        )

    return scorer
