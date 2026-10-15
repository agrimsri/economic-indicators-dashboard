
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(_REPO_ROOT / ".env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Economic Indicators Dashboard API"
    app_version: str = "1.0.0"
    app_env: str = "development"
    log_level: str = "info"

    # Database
    database_url: str = Field(
        default="postgresql://app_user:password@127.0.0.1:5434/economic_dashboard",
        description="PostgreSQL connection string bound to localhost/private network"
    )
    db_pool_min_size: int = 2
    db_pool_max_size: int = 10

    # Auth & Security
    jwt_secret: str = Field(
        default="0" * 64,
        description="Secret key for signing access JWTs"
    )
    jwt_algorithm: str = "HS256"
    jwt_access_ttl_min: int = 15
    jwt_refresh_ttl_days: int = 7

    # CORS & Cookies
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    cookie_domain: str = "localhost"
    cookie_secure: bool = False
    cookie_samesite: str = "lax"

    # Collector settings
    enable_scheduler: bool = True
    nse_base_url: str = "https://www.nseindia.com"
    nse_poll_seconds_open: int = 20
    nse_poll_seconds_closed: int = 600
    http_timeout_connect: int = 10
    http_timeout_read: int = 20

    # Optional public keys
    data_gov_in_api_key: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
