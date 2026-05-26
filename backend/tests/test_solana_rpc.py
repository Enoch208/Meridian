from meridian.datafeed.solana_rpc import parse_authorities
from meridian.datafeed.models import UNKNOWN


def test_parse_authorities():
    renounced = {
        "result": {
            "value": {
                "data": {
                    "parsed": {
                        "info": {"mintAuthority": None, "freezeAuthority": None}
                    }
                }
            }
        }
    }
    assert parse_authorities(renounced) == ("renounced", "renounced")

    live = {
        "result": {
            "value": {
                "data": {
                    "parsed": {
                        "info": {"mintAuthority": "Abc", "freezeAuthority": None}
                    }
                }
            }
        }
    }
    assert parse_authorities(live) == ("live:Abc", "renounced")

    assert parse_authorities({"result": {"value": None}}) == (UNKNOWN, UNKNOWN)
