"""Smart-money scout: deterministic candidate scoring against the watchlist."""
from meridian.datafeed.models import Candidate
from meridian.datafeed.smart_money.models import SmartMoneyWallet, WalletObservation
from meridian.scouts import smart_money as sm


def _c(addr="MINT1"):
    return Candidate(address=addr, name="x", symbol="X", pair_url="u")


def _w(addr, score=70.0, label=None, is_curated=False):
    return SmartMoneyWallet(address=addr, score=score, label=label, is_curated=is_curated)


def test_unknown_when_no_watchlist():
    score, reasons, unknowns = sm.score_candidate(_c(), [], helius_key="k")
    assert score is None
    assert "smart_money" in unknowns


def test_unknown_when_no_helius_key():
    score, reasons, unknowns = sm.score_candidate(_c(), [_w("A")], helius_key=None)
    assert score is None
    assert "smart_money" in unknowns


def test_unknown_when_no_address():
    c = Candidate(address="", name="x", symbol="X", pair_url="u")
    score, _, unknowns = sm.score_candidate(c, [_w("A")], helius_key="k")
    assert score is None
    assert "smart_money" in unknowns


def test_low_score_when_chain_data_present_but_no_overlap(monkeypatch):
    """Chain data here, watchlist here, no smart money showed up = honest 25."""
    fake_buyers = [WalletObservation(address="UNKNOWN", source="helius:earliest_buyers",
                                     token_mint="MINT1", rank=1)]
    monkeypatch.setattr(sm.helius, "fetch_earliest_buyers", lambda *a, **kw: fake_buyers)
    score, reasons, unknowns = sm.score_candidate(_c(), [_w("WATCH")], helius_key="k")
    assert score == 25
    assert unknowns == []


def test_unknown_when_helius_returns_nothing(monkeypatch):
    monkeypatch.setattr(sm.helius, "fetch_earliest_buyers", lambda *a, **kw: [])
    score, _, unknowns = sm.score_candidate(_c(), [_w("WATCH")], helius_key="k")
    assert score is None
    assert "smart_money" in unknowns


def test_one_watchlist_hit_produces_real_score(monkeypatch):
    buyers = [
        WalletObservation(address="OTHER", source="helius:earliest_buyers", token_mint="MINT1", rank=1),
        WalletObservation(address="WHALE_A", source="helius:earliest_buyers", token_mint="MINT1", rank=2),
        WalletObservation(address="OTHER2", source="helius:earliest_buyers", token_mint="MINT1", rank=3),
    ]
    monkeypatch.setattr(sm.helius, "fetch_earliest_buyers", lambda *a, **kw: buyers)
    score, reasons, unknowns = sm.score_candidate(
        _c(), [_w("WHALE_A", score=80, label="ansem")], helius_key="k",
    )
    assert score is not None and score >= 30
    assert any("ansem" in r for r in reasons)
    assert unknowns == []


def test_more_hits_outrank_fewer(monkeypatch):
    """Breadth dominates the score: 3 hits beat 1 hit at equal wallet quality."""
    def fake(mint, *, api_key, limit, client=None):
        if mint == "MINT_BROAD":
            return [WalletObservation(address=f"W{i}", source="helius:earliest_buyers",
                                      token_mint=mint, rank=i) for i in range(1, 5)]
        return [WalletObservation(address="W1", source="helius:earliest_buyers",
                                  token_mint=mint, rank=2)]

    monkeypatch.setattr(sm.helius, "fetch_earliest_buyers", fake)
    watch = [_w(f"W{i}", score=70) for i in range(1, 5)]
    broad, _, _ = sm.score_candidate(_c("MINT_BROAD"), watch, helius_key="k")
    thin, _, _ = sm.score_candidate(_c("MINT_THIN"), watch, helius_key="k")
    assert broad > thin


def test_make_scorer_closes_over_watchlist_and_key(monkeypatch):
    monkeypatch.setattr(sm.helius, "fetch_earliest_buyers", lambda *a, **kw: [
        WalletObservation(address="W", source="helius:earliest_buyers",
                          token_mint="MINT1", rank=1),
    ])
    scorer = sm.make_scorer([_w("W", score=80, label="curated")], helius_key="k")
    score, reasons, unknowns = scorer(_c("MINT1"))
    assert score is not None
    assert unknowns == []
