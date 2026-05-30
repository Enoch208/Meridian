"""TTL cache: hit/miss/eviction + safe path sanitization."""
import json

from meridian.datafeed.smart_money import cache
from meridian.datafeed.smart_money.models import WalletObservation


def _obs(addr="A"):
    return WalletObservation(address=addr, source="helius:earliest_buyers",
                             token_mint="M", rank=1)


def test_miss_when_absent(tmp_path):
    assert cache.cached_observations(str(tmp_path), "src", "k") is None


def test_round_trip_within_ttl(tmp_path):
    cache.write_observations(str(tmp_path), "src", "k", [_obs("A"), _obs("B")])
    got = cache.cached_observations(str(tmp_path), "src", "k", ttl_s=60)
    assert got is not None
    assert [o.address for o in got] == ["A", "B"]


def test_miss_when_stale(tmp_path):
    cache.write_observations(str(tmp_path), "src", "k", [_obs("A")])
    # Tampered timestamp = way in the past
    p = cache._cache_path(str(tmp_path), "src", "k")
    wrapper = json.loads(p.read_text())
    wrapper["fetched_at_epoch"] = 0
    p.write_text(json.dumps(wrapper))
    assert cache.cached_observations(str(tmp_path), "src", "k", ttl_s=60) is None


def test_corrupt_cache_returns_none(tmp_path):
    p = cache._cache_path(str(tmp_path), "src", "k")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("{not json")
    assert cache.cached_observations(str(tmp_path), "src", "k") is None


def test_path_sanitization_blocks_traversal(tmp_path):
    """A malicious mint string mustn't escape DATA_DIR/cache/."""
    p = cache._cache_path(str(tmp_path), "src", "../../../etc/passwd")
    # The mint key collapses unsafe chars and the path stays under tmp_path.
    assert tmp_path in p.parents or p.is_relative_to(tmp_path)
    assert "passwd" in p.name  # the safe-fied tail


def test_drops_unknown_fields_on_load(tmp_path):
    """If we add a new column later, old cache files should still load."""
    p = cache._cache_path(str(tmp_path), "src", "k")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({
        "fetched_at_epoch": 99_999_999_999,  # far future = always fresh
        "data": [{"address": "A", "source": "curated", "future_field": "x"}],
    }))
    got = cache.cached_observations(str(tmp_path), "src", "k", ttl_s=60)
    assert got and got[0].address == "A"
