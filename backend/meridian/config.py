"""Runtime settings loaded from environment / .env."""
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    swarms_api_key: str
    model: str
    solana_rpc_url: str
    dex_min_liquidity_usd: float
    dex_max_age_hours: float
    data_dir: str
    api_port: int
    run_secret: str
    # Durable storage — when mongodb_uri is set, the shortlist + call log are
    # persisted to MongoDB (survives Render restarts) instead of the local disk.
    mongodb_uri: str
    mongodb_db: str


def get_settings() -> Settings:
    return Settings(
        swarms_api_key=os.getenv("SWARMS_API_KEY", ""),
        model=os.getenv("MERIDIAN_MODEL", "gpt-4o-mini"),
        solana_rpc_url=os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com"),
        dex_min_liquidity_usd=float(os.getenv("DEX_MIN_LIQUIDITY_USD", "5000")),
        dex_max_age_hours=float(os.getenv("DEX_MAX_AGE_HOURS", "48")),
        data_dir=os.getenv("DATA_DIR", "./data"),
        api_port=int(os.getenv("MERIDIAN_API_PORT", "8000")),
        run_secret=os.getenv("MERIDIAN_RUN_SECRET", ""),
        mongodb_uri=os.getenv("MONGODB_URI", ""),
        mongodb_db=os.getenv("MONGODB_DB", "meridian"),
    )
