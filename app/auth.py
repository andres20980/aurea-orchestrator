"""Authentication utilities for aurea-orchestrator."""
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from app.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)):
    """Verify API key for protected endpoints.
    
    Args:
        api_key: API key from request header
    
    Raises:
        HTTPException: If API key is invalid or missing
    """
    if not settings.api_key:
        # If no API key is configured, allow access
        return
    
    if not api_key or api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
