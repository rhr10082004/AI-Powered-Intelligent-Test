"""
Configuration management for FastAPI application.
"""

from functools import lru_cache
from typing import Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Application
    environment: str = "development"
    app_name: str = "Intelligent Test Prep Platform API"
    app_version: str = "0.1.0"
    api_prefix: str = "/api"
    frontend_url: str = "http://localhost:3000"
    debug: bool = True

    # Database
    database_url: str = "sqlite+aiosqlite:///./testprep.db"
    db_echo: bool = False

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: Optional[str] = None

    # JWT
    jwt_secret_key: str = "your_secret_key_here_change_in_production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    refresh_token_expiration_days: int = 7
    admin_api_key: Optional[str] = None

    # CORS
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
    ]

    # OpenAI
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    openai_embedding_model: str = "text-embedding-3-small"

    # Email (Optional)
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    sender_email: str = "noreply@testprep.local"

    # Storage
    s3_bucket: str = "testprep-uploads"
    s3_region: str = "us-east-1"
    s3_access_key_id: Optional[str] = None
    s3_secret_access_key: Optional[str] = None
    s3_endpoint_url: Optional[str] = None

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Feature Flags
    enable_mock_llm: bool = False
    enable_analytics: bool = True
    enable_gamification: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False

    @model_validator(mode="after")
    def validate_production_settings(self):
        if self.environment.casefold() == "production":
            if self.jwt_secret_key == "your_secret_key_here_change_in_production" or len(self.jwt_secret_key) < 32:
                raise ValueError("JWT_SECRET_KEY must be a unique secret of at least 32 characters in production")
            if any("localhost" in origin or "127.0.0.1" in origin for origin in self.cors_origins):
                raise ValueError("CORS_ORIGINS must not contain localhost in production")
        return self


@lru_cache
def get_settings() -> Settings:
    """Get application settings (cached)."""
    return Settings()
