"""Configuration management for aurea-orchestrator."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    
    # Application settings
    app_name: str = "aurea-orchestrator"
    debug: bool = False
    
    # Redis settings
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_ssl: bool = False
    
    # Cache settings
    cache_enabled: bool = True
    cache_llm_ttl: int = 3600  # 1 hour in seconds
    cache_embedding_ttl: int = 86400  # 24 hours in seconds
    
    # API authentication
    api_key: Optional[str] = None
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000


settings = Settings()
