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
    """Deterministic ranking by liquidity — for tests, demos, and offline runs."""

    def rank(self, candidates: list[Candidate]) -> list[Pick]:
        ranked = sorted(candidates, key=lambda c: (c.liquidity_usd or 0), reverse=True)[:3]
        picks: list[Pick] = []
        for i, c in enumerate(ranked, start=1):
            liq = _scale(c.liquidity_usd, 50000)
            mom = _scale((c.buy_sell_ratio_h1() or 0) * 10000, 30000)
            onchain = 80 if c.mint_authority == "renounced" and c.freeze_authority == "renounced" else 50
            composite = int(round((liq + mom + onchain) / 3))
            picks.append(Pick(
                rank=i, candidate=c, composite_score=composite,
                scores={"onchain": onchain, "liquidity": liq, "momentum": mom, "smart_money": None},
                top_reasons=[f"Liquidity ${(c.liquidity_usd or 0):,.0f}",
                             f"Buy/sell {c.buy_sell_ratio_h1() or 0:.1f}x (1h)"],
                standout_risk=("Pair is young — unproven" if (c.age_hours or 0) < 24
                               else "Verify liquidity is locked"),
                one_line_read="Liquid and buyer-led — worth investigating.",
                unknowns=["smart_money"],
            ))
        return picks


def _scale(value: Optional[float], cap: float) -> int:
    if not value:
        return 0
    return max(0, min(100, int(round(value / cap * 100))))


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
                 base_url: str = SWARMS_API_BASE):
        from meridian.config import get_settings
        s = get_settings()
        self.model = model or s.model
        self.api_key = api_key or s.swarms_api_key
        self.base_url = base_url.rstrip("/")

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
        return parse_lead_json(_output_text(body.get("output")), candidates)
