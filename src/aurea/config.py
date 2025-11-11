"""Configuration management for Aurea Orchestrator."""

import os
from typing import Optional, List
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config(BaseModel):
    """Configuration for the Aurea Orchestrator."""
    
    # Cost limits
    MAX_JOB_COST: float = Field(
        default=float(os.getenv("MAX_JOB_COST", "10.0")),
        description="Maximum cost per job in USD before aborting"
    )
    
    # Rate limiting
    DEFAULT_RPM: int = Field(
        default=int(os.getenv("DEFAULT_RPM", "60")),
        description="Default requests per minute limit"
    )
    DEFAULT_TPM: int = Field(
        default=int(os.getenv("DEFAULT_TPM", "100000")),
        description="Default tokens per minute limit"
    )
    
    # Retry configuration
    MAX_RETRIES: int = Field(
        default=int(os.getenv("MAX_RETRIES", "3")),
        description="Maximum number of retry attempts"
    )
    RETRY_BASE_DELAY: float = Field(
        default=float(os.getenv("RETRY_BASE_DELAY", "1.0")),
        description="Base delay in seconds for exponential backoff"
    )
    RETRY_MAX_DELAY: float = Field(
        default=float(os.getenv("RETRY_MAX_DELAY", "60.0")),
        description="Maximum delay in seconds for exponential backoff"
    )
    
    # Circuit breaker
    CIRCUIT_BREAKER_THRESHOLD: int = Field(
        default=int(os.getenv("CIRCUIT_BREAKER_THRESHOLD", "5")),
        description="Number of failures before circuit opens"
    )
    CIRCUIT_BREAKER_TIMEOUT: float = Field(
        default=float(os.getenv("CIRCUIT_BREAKER_TIMEOUT", "60.0")),
        description="Timeout in seconds before attempting to close circuit"
    )
    
    # Model allow/deny lists
    ALLOWED_MODELS: Optional[List[str]] = Field(
        default=None,
        description="List of allowed models (None = all allowed)"
    )
    DENIED_MODELS: Optional[List[str]] = Field(
        default=None,
        description="List of denied models (takes precedence over allowed)"
    )
    
    # Logging
    LOG_LEVEL: str = Field(
        default=os.getenv("LOG_LEVEL", "INFO"),
        description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )
    REDACT_PII: bool = Field(
        default=os.getenv("REDACT_PII", "true").lower() == "true",
        description="Whether to redact PII in logs"
    )
    
    def __init__(self, **kwargs):
        """Initialize configuration with environment variable parsing."""
        # Parse allowed models from comma-separated env var
        if "ALLOWED_MODELS" not in kwargs:
            allowed_models_env = os.getenv("ALLOWED_MODELS")
            if allowed_models_env:
                kwargs["ALLOWED_MODELS"] = [
                    m.strip() for m in allowed_models_env.split(",")
                ]
        
        # Parse denied models from comma-separated env var
        if "DENIED_MODELS" not in kwargs:
            denied_models_env = os.getenv("DENIED_MODELS")
            if denied_models_env:
                kwargs["DENIED_MODELS"] = [
                    m.strip() for m in denied_models_env.split(",")
                ]
        
        super().__init__(**kwargs)
    
    def is_model_allowed(self, model_name: str) -> bool:
        """Check if a model is allowed to be used."""
        # Deny list takes precedence
        if self.DENIED_MODELS and model_name in self.DENIED_MODELS:
            return False
        
        # If allow list is set, model must be in it
        if self.ALLOWED_MODELS:
            return model_name in self.ALLOWED_MODELS
        
        # No restrictions
        return True


# Global config instance
config = Config()
