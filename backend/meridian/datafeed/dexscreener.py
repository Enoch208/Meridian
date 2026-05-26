import time
import httpx

from .models import Candidate

BASE = "https://api.dexscreener.com"


def parse_token_pairs(raw: dict) -> list[Candidate]:
    pairs = [p for p in raw.get("pairs", []) if p.get("chainId") == "solana"]
    pairs.sort(key=lambda p: (p.get("liquidity") or {}).get("usd", 0), reverse=True)
    out = []
    for p in pairs[:1]:  # best pair per token
        bt = p.get("baseToken", {})
        created = p.get("pairCreatedAt")
        age = (time.time() * 1000 - created) / 3_600_000 if created else None
        txh1 = (p.get("txns") or {}).get("h1") or {}
        vol = p.get("volume") or {}
        out.append(
            Candidate(
                address=bt.get("address", ""),
                name=bt.get("name", ""),
                symbol=bt.get("symbol", ""),
                pair_url=p.get("url", ""),
                liquidity_usd=(p.get("liquidity") or {}).get("usd"),
                fdv=p.get("fdv"),
                market_cap=p.get("marketCap"),
                age_hours=age,
                volume_h24=vol.get("h24"),
                volume_h6=vol.get("h6"),
                volume_h1=vol.get("h1"),
                buys_h1=txh1.get("buys"),
                sells_h1=txh1.get("sells"),
                price_usd=float(p["priceUsd"]) if p.get("priceUsd") else None,
            )
        )
    return out


def fetch_recent_candidates(
    limit: int = 30, client: httpx.Client | None = None
) -> list[Candidate]:
    c = client or httpx.Client(timeout=20)
    profiles = c.get(f"{BASE}/token-profiles/latest/v1").json()
    addrs = [
        p["tokenAddress"] for p in profiles if p.get("chainId") == "solana"
    ][:limit]
    cands = []
    for a in addrs:
        try:
            cands += parse_token_pairs(c.get(f"{BASE}/latest/dex/tokens/{a}").json())
        except Exception:
            continue
    return cands
