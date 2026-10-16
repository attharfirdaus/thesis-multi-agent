"""Settings, read from the environment only. No secret has a default in production."""

from functools import lru_cache
from typing import Literal

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
    # "lax" when the frontend and API share a site (localhost, or one hostname).
    # "none" is required when the browser page and the API are on different sites
    # (e.g. a Vercel frontend calling a tunneled local API): browsers do not send a
    # SameSite=Lax cookie on a cross-site fetch, so the session would silently not arrive.
    # "none" is only accepted by browsers together with Secure=true.
    cookie_samesite: Literal["lax", "strict", "none"] = Field(default="lax", alias="COOKIE_SAMESITE")
    # Set to the hostname (e.g. example.duckdns.org) so cookies are not sent to other subdomains.
    cookie_domain: str | None = Field(default=None, alias="COOKIE_DOMAIN")

    login_max_attempts: int = Field(default=5, alias="LOGIN_MAX_ATTEMPTS")
    login_window_seconds: int = Field(default=900, alias="LOGIN_WINDOW_SECONDS")

    # Inference provider (phase 4). The provider URL and the model live here and never in code
    # (PRD §8), so a route can be swapped without a deploy and a route whose free tier may train on
    # prompt content is never compiled in (PRD §7, O-6). Empty means "not configured yet":
    # `ProviderClient` refuses to call out instead of guessing a route, so a deployment that is
    # missing them fails loudly at the first agent step rather than half-succeeding.
    llm_base_url: str | None = Field(default=None, alias="LLM_BASE_URL")
    llm_api_key: str | None = Field(default=None, alias="LLM_API_KEY")
    llm_model: str | None = Field(default=None, alias="LLM_MODEL")
    # Reproducibility (PRD §11): both are stored per run, so they are settings and not call-site
    # constants. `seed` is best-effort on every free route evaluated, hence optional.
    llm_temperature: float = Field(default=0, alias="LLM_TEMPERATURE")
    llm_seed: int | None = Field(default=None, alias="LLM_SEED")
    # Invalid JSON and schema violations are retried, then the agent is marked failed (PRD §6), so
    # this is the total number of attempts, not the number of retries.
    llm_max_attempts: int = Field(default=3, alias="LLM_MAX_ATTEMPTS")
    llm_timeout_seconds: float = Field(default=120, alias="LLM_TIMEOUT_SECONDS")
    # A hard ceiling on generated tokens. Without one, generation is unbounded: asked to score a
    # 9k-character analysis on 2026-10-16, the model emitted for more than 300 seconds and produced
    # nothing, while the same prompt with a cap answered in 8 seconds. Legitimate answers measured on
    # real submissions are 750–1,046 characters (~200–260 tokens), so this leaves ~4x headroom.
    llm_max_tokens: int = Field(default=1024, alias="LLM_MAX_TOKENS")

    @property
    def is_production(self) -> bool:
        return self.env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
