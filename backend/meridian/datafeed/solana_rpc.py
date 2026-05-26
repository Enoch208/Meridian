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
