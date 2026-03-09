from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Proweb Signal Engine"
    environment: str = "dev"
    log_level: str = "INFO"

    postgres_dsn: str = Field(default="postgresql+psycopg://postgres:postgres@localhost:5432/proweb")
    redis_url: str = Field(default="redis://localhost:6379/0")

    binance_api_key: str = ""
    binance_api_secret: str = ""
    binance_base_url: str = "https://api.binance.com"

    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    llm_provider: str = "disabled"

    low_volume_min: float = 100_000
    low_volume_max: float = 500_000
    mid_volume_max: float = 5_000_000

    max_entry_zone_width_pct: float = 0.008
    abnormal_stop_loss_pct: float = 0.04
    min_confidence_score: int = 65

    # Risk / leverage controls
    max_leverage: float = 10.0
    target_risk_per_trade_pct: float = 0.02

    # Event data adapters (optional)
    rootdata_events_url: str = ""
    cmc_unlocks_url: str = ""
    coingecko_events_url: str = "https://api.coingecko.com/api/v3/coins/{symbol}/status_updates"


settings = Settings()
