"""ScoutSwarm: turns scored candidates into a ranked shortlist.

`SwarmsScoutSwarm` is the real multi-agent implementation (lazy-imports
`swarms` so this module loads without the optional dependency). `MockScoutSwarm`
is a deterministic stand-in used by the pipeline/CLI tests so nothing depends on
spending Swarms credit.
"""
from __future__ import annotations

import dataclasses
import json
import re
from typing import Optional, Protocol

from meridian.datafeed.models import UNKNOWN, Candidate, Pick


class SwarmError(RuntimeError):
    """Raised when the real swarm fails to produce parseable output."""


class ScoutSwarm(Protocol):
    def rank(self, candidates: list[Candidate]) -> list[Pick]:
        ...


def to_agent_payload(c: Candidate) -> dict:
    """Serialize a Candidate for an agent; every missing field becomes Unknown."""
    payload = {}
    for f in dataclasses.fields(c):
        val = getattr(c, f.name)
        payload[f.name] = UNKNOWN if val is None else val
    payload["buy_sell_ratio_h1"] = c.buy_sell_ratio_h1() if c.buy_sell_ratio_h1() is not None else UNKNOWN
    payload["liq_to_fdv"] = c.liq_to_fdv() if c.liq_to_fdv() is not None else UNKNOWN
    return payload


def _index(cands: list[Candidate]) -> dict[str, Candidate]:
    idx: dict[str, Candidate] = {}
    for c in cands:
        if c.symbol:
            idx.setdefault(c.symbol, c)
        if c.address:
            idx.setdefault(c.address, c)
    return idx


def _json_arrays(text: str) -> list:
    """Return every balanced top-level [...] substring that parses as JSON."""
    out = []
    depth = 0
    start = -1
    for i, ch in enumerate(text):
        if ch == "[":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "]" and depth > 0:
            depth -= 1
            if depth == 0 and start >= 0:
                try:
                    out.append(json.loads(text[start:i + 1]))
                except json.JSONDecodeError:
                    pass
                start = -1
    return out


def parse_lead_json(text: str, candidates: list[Candidate]) -> list[Pick]:
    """Extract the lead agent's JSON array and map it onto Candidate objects.

    Robust to the lead's array being embedded in a longer conversation /
    markdown: scans for balanced ``[...]`` blocks and uses the last one that
    looks like a list of pick objects.
    """
    arrays = [a for a in _json_arrays(text)
              if isinstance(a, list) and a and isinstance(a[0], dict)
              and ("symbol" in a[0] or "address" in a[0] or "rank" in a[0])]
    if not arrays:
        raise SwarmError(f"no pick JSON array in lead output: {text[:200]!r}")
    rows = arrays[-1]
    idx = _index(candidates)
    picks: list[Pick] = []
    for pos, row in enumerate(rows):
        cand = idx.get(row.get("symbol")) or idx.get(row.get("address"))
        if cand is None:
            # Fallback: scan the row's text for a candidate symbol or name.
            blob = json.dumps(row).lower()
            cand = next((c for c in candidates
                         if (c.symbol and c.symbol.lower() in blob)
                         or (c.name and c.name.lower() in blob)), None)
        if cand is None and len(rows) <= len(candidates):
            # Last resort: positional match (lead preserves our candidate order).
            cand = candidates[pos] if pos < len(candidates) else None
        if cand is None:
            continue
        scores = row.get("scores", {}) or {}
        scores.setdefault("smart_money", None)
        unknowns = row.get("unknowns") or []
        if "smart_money" not in unknowns:
            unknowns = [*unknowns, "smart_money"]
        picks.append(Pick(
            rank=int(row.get("rank", len(picks) + 1)),
            candidate=cand,
            composite_score=int(row.get("composite_score", 0)),
            scores=scores,
            top_reasons=row.get("top_reasons", []),
            standout_risk=row.get("standout_risk", ""),
            one_line_read=row.get("one_line_read", ""),
            unknowns=unknowns,
        ))
    if not picks:
        raise SwarmError("lead JSON matched no candidates")
    picks.sort(key=lambda p: p.rank)
    return picks


class MockScoutSwarm:
    """Deterministic, honesty-aware ranking — for tests, demos, and the
    on-demand /api/evaluate path. Missing signals score Unknown (None) and are
    excluded from the composite (never invented as 0). Ranks by liquidity.

    If a ``smart_money_scorer`` is supplied (see ``meridian.scouts.smart_money``)
    each candidate's ``smart_money`` sub-score is populated deterministically
    from the watchlist; otherwise it stays Unknown — same honest semantics.
    """

    def __init__(self, smart_money_scorer=None):
        # Signature: (Candidate) -> (Optional[int] score, list[str] reasons, list[str] unknowns)
        self.smart_money_scorer = smart_money_scorer

    def rank(self, candidates: list[Candidate]) -> list[Pick]:
        ranked = sorted(candidates, key=lambda c: (c.liquidity_usd or 0), reverse=True)[:3]
        return [
            _score_candidate(c, i, smart_money_scorer=self.smart_money_scorer)
            for i, c in enumerate(ranked, start=1)
        ]


def _scale(value: Optional[float], cap: float) -> int:
    if not value:
        return 0
    return max(0, min(100, int(round(value / cap * 100))))


def _score_candidate(c: Candidate, rank: int, *, smart_money_scorer=None) -> Pick:
    """Score one candidate honestly: verifiable signals get a 0–100 score,
    unverifiable ones are Unknown (None) and excluded from the composite."""
    reasons: list[str] = []
    unknowns: list[str] = []

    # On-chain — authorities; Unknown when neither is verifiable (the model's
    # default is the string "Unknown", not None).
    mint_known = c.mint_authority not in (None, UNKNOWN)
    freeze_known = c.freeze_authority not in (None, UNKNOWN)
    mint_ok = c.mint_authority == "renounced"
    freeze_ok = c.freeze_authority == "renounced"
    if not mint_known and not freeze_known:
        onchain: Optional[int] = None
        unknowns.append("onchain")
    elif mint_ok and freeze_ok:
        onchain = 85
        reasons.append("Mint & freeze authority renounced")
    elif mint_ok or freeze_ok:
        onchain = 55
        reasons.append("One authority still live — partial risk")
    else:
        onchain = 20
        reasons.append("Mint/freeze authority live — rug risk")

    # Liquidity — null is Unknown, never reported as $0.
    if c.liquidity_usd is None:
        liquidity: Optional[int] = None
        unknowns.append("liquidity")
    else:
        liquidity = _scale(c.liquidity_usd, 50000)
        if c.liquidity_usd >= 25000:
            reasons.append(f"Healthy liquidity ${c.liquidity_usd:,.0f}")
        else:
            reasons.append(f"Thin liquidity ${c.liquidity_usd:,.0f}")

    # Momentum — buy/sell pressure + 24h price trend, dampened by how much
    # volume actually backs it. Thin volume = low confidence, not strong
    # momentum (a 9:1 ratio on $900 of volume is noise, not a signal).
    ratio = c.buy_sell_ratio_h1()
    change = c.price_change_24h
    vol = c.volume_h24
    if ratio is None and change is None and not vol:
        momentum: Optional[int] = None
        unknowns.append("momentum")
    else:
        pressure = 50.0
        if ratio is not None:
            pressure = 50 + (ratio - 1) * 20  # neutral 1.0 → 50; 3.5x → 100
        if change is not None:
            pressure += max(-25.0, min(25.0, change / 4))  # price-trend nudge
        pressure = max(0.0, min(100.0, pressure))
        confidence = min(1.0, (vol or 0) / 25000)  # ~$25k 24h vol = full weight
        momentum = int(round(pressure * (0.45 + 0.55 * confidence)))
        if ratio is not None and ratio >= 1.3:
            reasons.append(f"Buyer-led {ratio:.1f}x buy/sell (1h)")
        elif vol:
            reasons.append(f"${vol:,.0f} 24h volume")

    # Smart-money — real deterministic score when a watchlist + Helius key are
    # configured; otherwise Unknown (no invention).
    smart_money: Optional[int] = None
    if smart_money_scorer is not None:
        try:
            smart_money, sm_reasons, sm_unknowns = smart_money_scorer(c)
        except Exception:  # pragma: no cover - defensive
            smart_money, sm_reasons, sm_unknowns = None, [], ["smart_money"]
        reasons.extend(sm_reasons)
        unknowns.extend(sm_unknowns)
    else:
        unknowns.append("smart_money")

    available = [s for s in (onchain, liquidity, momentum, smart_money) if s is not None]
    composite = int(round(sum(available) / len(available))) if available else 0
    # Absence of evidence is a mild negative: unverified liquidity caps the
    # score so it can never read as "clean" without it.
    if liquidity is None:
        composite = min(composite, 70)

    if liquidity is None:
        risk = "Liquidity unverified — could be thin"
    elif c.liquidity_usd is not None and c.liquidity_usd < 10000:
        risk = "Thin liquidity — exit-rug risk"
    elif onchain is not None and onchain < 50:
        risk = "Authorities not renounced — rug risk"
    elif (c.age_hours or 0) < 24:
        risk = "Pair is young — unproven"
    else:
        risk = "Verify liquidity is locked before sizing up"

    if composite >= 75:
        read = "Clean signals across the board — worth investigating."
    elif composite >= 55:
        read = "Mixed signals with upside — worth investigating with care."
    else:
        read = "Weak or unverified signals — investigate cautiously."

    return Pick(
        rank=rank,
        candidate=c,
        composite_score=composite,
        scores={
            "onchain": onchain,
            "liquidity": liquidity,
            "momentum": momentum,
            "smart_money": smart_money,
        },
        top_reasons=reasons[:2] or ["Limited data available"],
        standout_risk=risk,
        one_line_read=read,
        unknowns=unknowns,
    )


SWARMS_API_BASE = "https://api.swarms.world"


def _output_text(output) -> str:
    """Flatten the Swarms API `output` (str | list[{role,content}] | dict) to text."""
    if isinstance(output, str):
        return output
    if isinstance(output, list):
        parts = []
        for m in output:
            if isinstance(m, dict):
                parts.append(str(m.get("content", "")))
            else:
                parts.append(str(m))
        return "\n".join(parts)
    return json.dumps(output)


class SwarmsScoutSwarm:
    """Real Swarms multi-agent swarm via the cloud API (Frenzy-Mode, zero-cost).

    Posts a SequentialWorkflow spec (3 scouts -> synthesizing lead) to
    ``POST /v1/swarm/completions`` with the ``x-api-key`` header. Uses the
    SWARMS_API_KEY only — no local model provider key required.
    """

    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None,
                 base_url: str = SWARMS_API_BASE, smart_money_scorer=None):
        from meridian.config import get_settings
        s = get_settings()
        self.model = model or s.model
        self.api_key = api_key or s.swarms_api_key
        self.base_url = base_url.rstrip("/")
        # Optional smart-money scorer (Callable[[Candidate], (score, reasons, unknowns)]).
        # When set, we override the LLM's smart_money values with deterministic
        # ones — the lead does composite/narrative, the watchlist does signal.
        self.smart_money_scorer = smart_money_scorer

    def _spec(self, candidates: list[Candidate]) -> dict:
        from meridian.scouts.prompts import SCOUT_PROMPTS, LEAD_PROMPT
        payloads = json.dumps([to_agent_payload(c) for c in candidates], indent=2)
        agents = [
            {"agent_name": f"{name}_scout", "system_prompt": prompt,
             "model_name": self.model, "max_loops": 1}
            for name, prompt in SCOUT_PROMPTS.items()
        ]
        agents.append({"agent_name": "scout_lead", "system_prompt": LEAD_PROMPT,
                       "model_name": self.model, "max_loops": 1})
        return {
            "name": "Meridian Scout Swarm",
            "description": "Scores recent Solana launches and synthesizes a ranked shortlist.",
            "swarm_type": "SequentialWorkflow",
            "max_loops": 1,
            "agents": agents,
            "task": (f"Recent Solana token candidates (Unknown = signal unavailable, "
                     f"down-weight it, never invent):\n{payloads}\n\n"
                     "Each scout: analyze only your own signals. "
                     "scout_lead: output ONLY the strict JSON array of the ranked top-3."),
        }

    def rank(self, candidates: list[Candidate]) -> list[Pick]:
        import httpx
        if not self.api_key:
            raise SwarmError("SWARMS_API_KEY is not set")
        try:
            resp = httpx.post(
                f"{self.base_url}/v1/swarm/completions",
                headers={"x-api-key": self.api_key, "Content-Type": "application/json"},
                json=self._spec(candidates),
                timeout=180,
            )
            resp.raise_for_status()
            body = resp.json()
        except SwarmError:
            raise
        except Exception as e:
            raise SwarmError(f"swarm API call failed: {e}") from e
        picks = parse_lead_json(_output_text(body.get("output")), candidates)
        if self.smart_money_scorer is not None:
            _apply_smart_money(picks, self.smart_money_scorer)
        return picks


def _apply_smart_money(picks: list[Pick], scorer) -> None:
    """Overlay deterministic smart-money scores on the LLM's output.

    The lead synthesizes the narrative; the watchlist owns the smart-money
    signal. Pick.scores['smart_money'] gets replaced (or kept None on
    Unknown), the 'smart_money' entry is removed from ``unknowns`` when the
    score is real, and any new reasons are appended (capped so we don't
    bloat the card).
    """
    for p in picks:
        try:
            score, reasons, unknowns = scorer(p.candidate)
        except Exception:  # pragma: no cover - defensive
            continue
        p.scores["smart_money"] = score
        if score is not None:
            p.unknowns = [u for u in p.unknowns if u != "smart_money"]
        else:
            if "smart_money" not in p.unknowns:
                p.unknowns = [*p.unknowns, "smart_money"]
        if reasons:
            existing = set(p.top_reasons)
            for r in reasons:
                if r not in existing and len(p.top_reasons) < 4:
                    p.top_reasons.append(r)
                    existing.add(r)
        # Refresh the composite to reflect the new sub-score.
        available = [v for v in p.scores.values() if isinstance(v, int)]
        if available:
            p.composite_score = int(round(sum(available) / len(available)))
