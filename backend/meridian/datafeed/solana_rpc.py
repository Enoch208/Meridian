import httpx

from .models import UNKNOWN


def parse_authorities(resp: dict) -> tuple[str, str]:
    try:
        info = resp["result"]["value"]["data"]["parsed"]["info"]
    except (KeyError, TypeError):
        return (UNKNOWN, UNKNOWN)

    def fmt(v):
        return "renounced" if v in (None, "") else f"live:{v}"

    return (fmt(info.get("mintAuthority")), fmt(info.get("freezeAuthority")))


def fetch_authorities(
    mint: str, rpc_url: str, client: httpx.Client | None = None
) -> tuple[str, str]:
    c = client or httpx.Client(timeout=15)
    body = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getAccountInfo",
        "params": [mint, {"encoding": "jsonParsed"}],
    }
    try:
        return parse_authorities(c.post(rpc_url, json=body).json())
    except Exception:
        return (UNKNOWN, UNKNOWN)


def fetch_owner_token_balance(
    owner: str, mint: str, rpc_url: str, client: httpx.Client | None = None
) -> float | None:
    """Sum a wallet's token balance (uiAmount) for a mint, or None on failure.

    Used to compute the dev wallet's holding %. Needs an RPC that supports
    getTokenAccountsByOwner (public mainnet-beta does).
    """
    c = client or httpx.Client(timeout=15)
    body = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenAccountsByOwner",
        "params": [owner, {"mint": mint}, {"encoding": "jsonParsed"}],
    }
    try:
        resp = c.post(rpc_url, json=body).json()
        accounts = resp["result"]["value"]
        total = 0.0
        for acc in accounts:
            amt = acc["account"]["data"]["parsed"]["info"]["tokenAmount"]["uiAmount"]
            total += amt or 0
        return total
    except Exception:
        return None
