"""Settings, read from the environment only. No secret has a default in production."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    env: str = Field(default="development")
    # Runtime role: it is NOT the table owner, so row-level security applies to it.
    database_url: str = Field(alias="DATABASE_URL")
    # Owner role, used only by scripts/migrate.py.
    migration_database_url: str | None = Field(default=None, alias="MIGRATION_DATABASE_URL")

    allowed_origins: list[str] = Field(default=["http://localhost:3000"], alias="ALLOWED_ORIGINS")

    session_cookie_name: str = Field(default="ta_session", alias="SESSION_COOKIE_NAME")
    csrf_cookie_name: str = Field(default="ta_csrf", alias="CSRF_COOKIE_NAME")
    session_ttl_days: int = Field(default=14, alias="SESSION_TTL_DAYS")
    # Must be true on the real host (HTTPS). False is for local http development only.
    cookie_secure: bool = Field(default=False, alias="COOKIE_SECURE")
    # Set to the hostname (e.g. example.duckdns.org) so cookies are not sent to other subdomains.
    cookie_domain: str | None = Field(default=None, alias="COOKIE_DOMAIN")

    login_max_attempts: int = Field(default=5, alias="LOGIN_MAX_ATTEMPTS")
    login_window_seconds: int = Field(default=900, alias="LOGIN_WINDOW_SECONDS")

    @property
    def is_production(self) -> bool:
        return self.env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
