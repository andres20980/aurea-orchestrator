"""Configuration management for Aurea Orchestrator."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # API Keys
    google_api_key: str = ""  # For Gemini
    openai_api_key: str = ""

    # Database
    database_url: str = "postgresql://aurea:aurea_pass@localhost:5432/aurea_orchestrator"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    # Model Configuration
    gemini_model: str = "gemini-1.5-pro"
    openai_model: str = "gpt-4"
    complexity_threshold: float = 0.5
    default_model_provider: str = "gemini"  # gemini or openai


settings = Settings()
