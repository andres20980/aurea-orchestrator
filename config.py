"""Configuration management for aurea-orchestrator."""
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    database_url: Optional[str] = None
    openai_api_key: str = ""
    embedding_model: str = "text-embedding-3-small"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
