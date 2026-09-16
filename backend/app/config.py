"""Application configuration management.

Handles environment variables, database settings, security parameters,
and application-wide configurations.
"""

from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application Info
    app_name: str = "CampusOS"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database
    database_url: str = "postgresql://user:password@localhost/campusos_db"
    database_echo: bool = False
    database_pool_size: int = 20
    database_max_overflow: int = 10
    database_pool_pre_ping: bool = True

    # Security
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # OAuth2
    oauth2_provider: str = "google"
    oauth2_client_id: Optional[str] = None
    oauth2_client_secret: Optional[str] = None
    oauth2_redirect_url: Optional[str] = None

    # Ollama (Local LLM)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama2"
    ollama_embedding_model: str = "nomic-embed-text"
    ollama_timeout: int = 300  # 5 minutes

    # Email
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "noreply@campusos.edu"
    smtp_from_name: str = "CampusOS"
    email_enabled: bool = True

    # File Upload
    max_upload_size: int = 52428800  # 50MB
    allowed_upload_types: list = [
        "pdf", "docx", "doc", "xlsx", "xls", "jpg", "jpeg", "png"
    ]
    upload_dir: str = "./uploads"

    # CORS
    cors_origins: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000"
    ]

    # Logging
    log_level: str = "INFO"
    log_file: str = "./logs/campusos.log"

    # Monitoring
    prometheus_enabled: bool = True
    prometheus_port: int = 8001

    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_period: int = 3600  # 1 hour

    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns:
        Settings: Application settings
    """
    return Settings()
