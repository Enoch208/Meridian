from .models import Candidate
from .solana_rpc import fetch_authorities


def enrich_authorities(cands: list[Candidate], rpc_url: str) -> list[Candidate]:
    for c in cands:
        if c.address:
            c.mint_authority, c.freeze_authority = fetch_authorities(c.address, rpc_url)
    return cands
