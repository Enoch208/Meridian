from meridian.datafeed.enrich import enrich_authorities
from meridian.datafeed.models import Candidate


def test_enrich_sets_authorities(monkeypatch):
    import meridian.datafeed.enrich as e

    monkeypatch.setattr(
        e, "fetch_authorities", lambda mint, url, client=None: ("renounced", "live:X")
    )
    c = Candidate(address="M", name="n", symbol="S", pair_url="u")
    [out] = enrich_authorities([c], "http://rpc")
    assert out.mint_authority == "renounced" and out.freeze_authority == "live:X"
