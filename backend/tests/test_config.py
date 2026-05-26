from meridian.config import get_settings


def test_settings_load_from_env(monkeypatch):
    monkeypatch.setenv("SWARMS_API_KEY", "sk-test")
    monkeypatch.setenv("DEX_MIN_LIQUIDITY_USD", "5000")
    s = get_settings()
    assert s.swarms_api_key == "sk-test"
    assert s.dex_min_liquidity_usd == 5000.0
    assert s.dex_max_age_hours > 0
