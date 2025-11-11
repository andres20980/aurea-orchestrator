"""Configuration management for Aurea Orchestrator."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # API Keys
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # Database
    database_url: str = "postgresql://aurea:aurea_pass@localhost:5432/aurea_orchestrator"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    # Model Configuration
    claude_model: str = "claude-3-sonnet-20240229"
    deepseek_model: str = "gpt-3.5-turbo"
    complexity_threshold: float = 0.5


settings = Settings()
