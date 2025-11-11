"""Configuration settings for Aurea Orchestrator"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/aurea_evals"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Evaluation
    default_accuracy_threshold: float = 0.8
    
    # Cost rates (per 1K tokens)
    cost_per_1k_input_tokens: float = 0.0001
    cost_per_1k_output_tokens: float = 0.0002
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
