from meridian.datafeed.smart_money.discover import aggregate
from meridian.datafeed.smart_money.models import WalletObservation


def _obs(addr, mint, *, source="helius:earliest_buyers", rank=None, pnl=None, notes=""):
    return WalletObservation(
        address=addr, source=source, token_mint=mint, rank=rank, pnl_usd=pnl, notes=notes
    )


def test_single_appearance_is_filtered_out():
    """One coincidence is not smart-money — the cross-token requirement is the gate."""
    obs = [_obs("WALLET_ONE_HIT", "MINT_A", rank=1)]
    assert aggregate(obs, min_appearances=2) == []


def test_two_distinct_tokens_qualifies_a_wallet():
    obs = [
        _obs("WIDE", "MINT_A", rank=2),
        _obs("WIDE", "MINT_B", rank=4),
    ]
    out = aggregate(obs, min_appearances=2)
    assert len(out) == 1
    w = out[0]
    assert w.address == "WIDE"
    assert w.winners_caught == 2
    assert w.avg_entry_rank == 3.0
    assert "helius:earliest_buyers" in w.sources
    assert not w.is_curated


def test_curated_wallets_pass_even_with_no_token_context():
    obs = [
        WalletObservation(address="HAND_PICKED", source="curated", notes="ansem"),
    ]
    out = aggregate(obs, min_appearances=2)
    assert len(out) == 1
    w = out[0]
    assert w.is_curated
    assert w.label == "ansem"
    assert w.score >= 70


def test_excluded_addresses_are_dropped():
    """System, DEX programs, burn sinks, wrapped SOL should never make the list."""
    excluded = [
        "11111111111111111111111111111111",         # System program
        "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",  # SPL Token program
        "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",  # Raydium AMM
        "So11111111111111111111111111111111111111112",   # Wrapped SOL mint
    ]
    obs = []
    for addr in excluded:
        obs.append(_obs(addr, "MINT_A", rank=1))
        obs.append(_obs(addr, "MINT_B", rank=2))
    assert aggregate(obs) == []


def test_score_rewards_early_entry_and_breadth():
    """A wallet that was rank 1 on 3 winners should outscore one that was rank
    20 on 2 winners."""
    early_broad = [
        _obs("EARLY", "MINT_A", rank=1),
        _obs("EARLY", "MINT_B", rank=2),
        _obs("EARLY", "MINT_C", rank=1),
    ]
    late_thin = [
        _obs("LATE", "MINT_A", rank=20),
        _obs("LATE", "MINT_B", rank=22),
    ]
    out = aggregate(early_broad + late_thin)
    by = {w.address: w for w in out}
    assert by["EARLY"].score > by["LATE"].score


def test_multi_source_observations_merge_under_one_wallet():
    obs = [
        _obs("WHALE", "MINT_A", source="helius:earliest_buyers", rank=3),
        _obs("WHALE", "MINT_A", source="birdeye:top_traders", rank=2, pnl=12000),
        _obs("WHALE", "MINT_B", source="helius:earliest_buyers", rank=5),
    ]
    out = aggregate(obs, min_appearances=2)
    assert len(out) == 1
    w = out[0]
    assert set(w.sources) == {"helius:earliest_buyers", "birdeye:top_traders"}
    assert w.winners_caught == 2  # MINT_A counts once across sources
    assert w.cumulative_pnl_usd == 12000


def test_output_is_sorted_by_score_descending():
    obs = [
        # Strong: rank 1 on 3 winners
        _obs("S1", "M1", rank=1), _obs("S1", "M2", rank=1), _obs("S1", "M3", rank=2),
        # Weaker: rank 25 on 2 winners
        _obs("W1", "M1", rank=25), _obs("W1", "M2", rank=26),
    ]
    out = aggregate(obs)
    assert [w.address for w in out] == ["S1", "W1"]
    assert out[0].score > out[1].score
