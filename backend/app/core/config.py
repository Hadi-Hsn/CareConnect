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
    database_url: str = "sqlite+aiosqlite:///./data/careconnect.db"

    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4o"
    openai_embedding_model: str = "text-embedding-3-large"
    openai_embedding_dimensions: int = 3072
    openai_max_tokens: int = 4096
    openai_temperature: float = 0.7
    
    # OpenAI Voice
    openai_tts_model: str = "tts-1"  # tts-1 or tts-1-hd
    openai_tts_voice: str = "alloy"  # alloy, echo, fable, onyx, nova, shimmer
    openai_stt_model: str = "whisper-1"

    # Vector Store
    vector_store_path: str = "./data/faiss_index"
    vector_store_type: Literal["faiss", "chromadb", "pgvector", "weaviate"] = "chromadb"
    
    # ChromaDB settings
    chroma_host: str = "chromadb"
    chroma_port: int = 8000
    chroma_collection_name: str = "careconnect_docs"

    # Email (SendGrid)
    sendgrid_api_key: str = ""
    email_from: str = "hadihacan@gmail.com"
    email_from_name: str = "CareConnect"

    # WhatsApp (Twilio)
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_number: str = ""  # Format: +14155238886 (Twilio Sandbox number)

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
        origins = [self.frontend_origin]
        
        # Add both http and https versions if not already included
        if self.frontend_origin.startswith("https://"):
            http_version = self.frontend_origin.replace("https://", "http://")
            if http_version not in origins:
                origins.append(http_version)
        elif self.frontend_origin.startswith("http://"):
            https_version = self.frontend_origin.replace("http://", "https://")
            if https_version not in origins:
                origins.append(https_version)
        
        # Add www subdomain variants
        domain = self.frontend_origin.split("://")[-1]
        if not domain.startswith("www."):
            if self.frontend_origin.startswith("https://"):
                origins.append(f"https://www.{domain}")
            if self.frontend_origin.startswith("http://"):
                origins.append(f"http://www.{domain}")
        
        return origins


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
