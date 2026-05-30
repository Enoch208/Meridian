import json

from meridian.datafeed.smart_money.curated import load_curated


def test_load_curated_skips_placeholders(tmp_path):
    path = tmp_path / "curated.json"
    path.write_text(json.dumps({
        "wallets": [
            {"address": "<replace-me>", "label": "skipme"},
            {"address": "RealWallet111", "label": "ansem"},
            {"address": "", "label": "blank"},
            {"address": "OtherWallet222"},
        ]
    }))

    obs = load_curated(str(path))
    assert [o.address for o in obs] == ["RealWallet111", "OtherWallet222"]
    assert obs[0].source == "curated"
    assert obs[0].notes == "ansem"


def test_load_curated_returns_empty_when_missing(tmp_path):
    assert load_curated(str(tmp_path / "nope.json")) == []
