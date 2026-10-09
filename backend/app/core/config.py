from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = Field(default="dev", alias="APP_ENV")
    database_url: str = Field(default="sqlite:///data/runtime/fraudmesh.db", alias="DATABASE_URL")
    data_dir: str = Field(default="data/demo", alias="DATA_DIR")
    jwt_secret: str = Field(default="change-me-generate-a-long-random-value", alias="JWT_SECRET")
    token_key_id: str = Field(default="fraudmesh-local-1", alias="TOKEN_KEY_ID")
    token_issuer: str = Field(default="fraudmesh", alias="TOKEN_ISSUER")
    token_audience: str = Field(default="fraudmesh-api", alias="TOKEN_AUDIENCE")
    session_minutes: int = Field(default=60, alias="SESSION_MINUTES")
    login_rate_limit_per_minute: int = Field(default=10, alias="LOGIN_RATE_LIMIT_PER_MINUTE")
    expensive_rate_limit_per_minute: int = Field(default=60, alias="EXPENSIVE_RATE_LIMIT_PER_MINUTE")
    max_request_body_bytes: int = Field(default=1_000_000, alias="MAX_REQUEST_BODY_BYTES")
    cors_origins: str = Field(default="http://localhost:5173,http://127.0.0.1:5173", alias="CORS_ORIGINS")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    demo_investigator_password: str = Field(default="", alias="DEMO_INVESTIGATOR_PASSWORD")
    demo_admin_password: str = Field(default="", alias="DEMO_ADMIN_PASSWORD")
    nemotron_base_url: str = Field(default="", alias="NEMOTRON_BASE_URL")
    nemotron_api_key: str = Field(default="", alias="NEMOTRON_API_KEY")
    nemotron_model: str = Field(default="", alias="NEMOTRON_MODEL")
    nemotron_timeout_s: float = Field(default=90.0, alias="NEMOTRON_TIMEOUT_S")
    nemotron_max_tokens: int = Field(default=2048, alias="NEMOTRON_MAX_TOKENS")

    @field_validator("app_env")
    @classmethod
    def validate_app_env(cls, value: str) -> str:
        if value not in {"dev", "demo", "prod"}:
            raise ValueError("APP_ENV must be dev, demo, or prod")
        return value

    def validate_runtime_secrets(self) -> None:
        placeholder = "change-me-generate-a-long-random-value"
        if self.app_env in {"demo", "prod"} and (
            self.jwt_secret == placeholder or len(self.jwt_secret) < 32
        ):
            raise ValueError("JWT_SECRET must be a non-placeholder 32-character secret in demo/prod")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_runtime_secrets()
    return settings
