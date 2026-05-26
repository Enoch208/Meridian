from meridian.datafeed.models import Candidate


def prefilter(cands: list[Candidate], min_liquidity_usd: float):
    kept, drops = [], []
    for c in cands:
        if c.liquidity_usd is not None and c.liquidity_usd < min_liquidity_usd:
            drops.append((c.symbol, f"liquidity ${c.liquidity_usd:.0f} below floor")); continue
        if c.mint_authority.startswith("live:") and c.freeze_authority.startswith("live:"):
            drops.append((c.symbol, "mint+freeze authority both live (rug-shaped)")); continue
        kept.append(c)
    return kept, drops
