"""Configuration models for the API Gateway."""
from pydantic import BaseModel, Field
from typing import Optional, List


class RateLimitConfig(BaseModel):
    """Rate limit configuration for an organization."""
    requests_per_minute: int = Field(default=60, ge=1)
    requests_per_hour: int = Field(default=1000, ge=1)


class OrgConfig(BaseModel):
    """Organization-specific configuration."""
    org_id: str
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    ip_allowlist: Optional[List[str]] = None  # None means all IPs allowed
    enabled: bool = True


class RateLimitUpdate(BaseModel):
    """Model for updating rate limits via admin endpoint."""
    org_id: str
    requests_per_minute: Optional[int] = Field(None, ge=1)
    requests_per_hour: Optional[int] = Field(None, ge=1)
