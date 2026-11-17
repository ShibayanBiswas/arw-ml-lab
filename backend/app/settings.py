"""Runtime settings from environment (.env / Render)."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(default="development", alias="APP_ENV")
    lab_default_seed: int = Field(default=42, alias="LAB_DEFAULT_SEED")
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    cors_allowed_origins: str = Field(default="http://localhost:3000", alias="CORS_ALLOWED_ORIGINS")
    supabase_url: str = Field(default="http://127.0.0.1:54321", alias="SUPABASE_URL")
    supabase_jwks_url: str = Field(
        default="http://127.0.0.1:54321/auth/v1/.well-known/jwks.json",
        alias="SUPABASE_JWKS_URL",
    )
    supabase_service_role_key: str = Field(default="", alias="SUPABASE_SERVICE_ROLE_KEY")
    database_url: str = Field(
        default="postgresql://postgres:postgres@127.0.0.1:54322/postgres",
        alias="DATABASE_URL",
    )
    # Session/direct pooler for workers, Optuna, long transactions (§39)
    database_url_session: str = Field(
        default="postgresql://postgres:postgres@127.0.0.1:54322/postgres",
        alias="DATABASE_URL_SESSION",
    )
    ai_enabled: bool = Field(default=False, alias="AI_ENABLED")
    service_role: str = Field(default="api", alias="SERVICE_ROLE")
    # When true, accept TEST_AUTH_* headers for unit tests (never in production)
    auth_test_bypass: bool = Field(default=False, alias="AUTH_TEST_BYPASS")
    # bff = jose HS256 from Next.js (ADR-0005); supabase = JWKS
    auth_mode: str = Field(default="bff", alias="AUTH_MODE")
    jwt_secret: str = Field(default="dev-jwt-secret-change-me", alias="JWT_SECRET")
    lab_default_workspace_id: str = Field(
        default="00000000-0000-0000-0000-000000000010",
        alias="LAB_DEFAULT_WORKSPACE_ID",
    )
    sentry_dsn: str = Field(default="", alias="SENTRY_DSN")
    sentry_environment: str = Field(default="development", alias="SENTRY_ENVIRONMENT")
    otel_enabled: bool = Field(default=False, alias="OTEL_ENABLED")
    otel_exporter_otlp_endpoint: str = Field(default="", alias="OTEL_EXPORTER_OTLP_ENDPOINT")
    otel_service_name: str = Field(default="lab-api", alias="OTEL_SERVICE_NAME")
    # Optuna RDB URL for resumable studies (§39.3); empty → DATABASE_URL_SESSION → in-memory
    optuna_storage_url: str = Field(default="", alias="OPTUNA_STORAGE_URL")

    def resolved_optuna_storage_url(self) -> str:
        """Prefer explicit OPTUNA_STORAGE_URL; else session pooler for workers."""
        if self.optuna_storage_url.strip():
            return self.optuna_storage_url.strip()
        if self.service_role.startswith("worker") and self.database_url_session.strip():
            return self.database_url_session.strip()
        return ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
