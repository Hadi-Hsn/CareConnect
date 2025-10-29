"""Core configuration for CareConnect backend."""
import secrets
from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    # Application
    app_name: str = "CareConnect"
    environment: Literal["development", "staging", "production"] = "development"
    log_level: str = "INFO"
    rate_limit_per_minute: int = 60

    # Database
    database_url: str = "sqlite+aiosqlite:///./careconnect.db"

    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4o"
    openai_embedding_model: str = "text-embedding-3-large"
    openai_embedding_dimensions: int = 3072
    openai_max_tokens: int = 4096
    openai_temperature: float = 0.7

    # Vector Store
    vector_store_path: str = "./data/faiss_index"
    vector_store_type: Literal["faiss", "pgvector", "weaviate"] = "faiss"

    # Email (SMTP only)
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    email_from: str = "noreply@careconnect.health"

    # Auth
    jwt_secret: str = secrets.token_urlsafe(32)
    jwt_issuer: str = "careconnect"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 1440
    oauth_provider: Literal["auth0", "email_otp"] = "email_otp"
    auth0_domain: str = ""
    auth0_client_id: str = ""
    auth0_client_secret: str = ""

    # CORS
    frontend_origin: str = "http://localhost:5173"

    # Features
    enable_prometheus: bool = True
    enable_privacy_mode: bool = False
    mock_scheduling: bool = True

    # Observability
    sentry_dsn: str = ""

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Ensure database URL is properly formatted."""
        if not v:
            raise ValueError("DATABASE_URL must be set")
        return v

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"

    @property
    def cors_origins(self) -> list[str]:
        """Get CORS allowed origins."""
        return [self.frontend_origin]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
