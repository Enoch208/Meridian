from meridian.scouts.prompts import SCOUT_PROMPTS, LEAD_PROMPT, HONESTY_RULES


def test_prompts_present_and_honest():
    assert set(SCOUT_PROMPTS) == {"onchain", "liquidity", "momentum"}
    for p in SCOUT_PROMPTS.values():
        assert HONESTY_RULES in p
    assert "worth investigating" in LEAD_PROMPT.lower()
    assert "json" in LEAD_PROMPT.lower()
