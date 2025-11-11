"""Rate limiting middleware."""
import time
from collections import defaultdict
from typing import Dict, Tuple
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.config_store import config_store


class RateLimitTracker:
    """Track rate limits per organization."""
    
    def __init__(self):
        # Structure: {org_id: {'minute': [(timestamp, count)], 'hour': [(timestamp, count)]}}
        self._requests: Dict[str, Dict[str, list]] = defaultdict(lambda: {'minute': [], 'hour': []})
    
    def _cleanup_old_entries(self, entries: list, window_seconds: int) -> list:
        """Remove entries older than the window."""
        current_time = time.time()
        return [(ts, count) for ts, count in entries if current_time - ts < window_seconds]
    
    def check_rate_limit(self, org_id: str, requests_per_minute: int, 
                        requests_per_hour: int) -> Tuple[bool, str]:
        """
        Check if request is within rate limits.
        Returns (is_allowed, reason_if_blocked).
        """
        current_time = time.time()
        org_data = self._requests[org_id]
        
        # Clean up old entries
        org_data['minute'] = self._cleanup_old_entries(org_data['minute'], 60)
        org_data['hour'] = self._cleanup_old_entries(org_data['hour'], 3600)
        
        # Count requests in the current windows
        minute_count = sum(count for _, count in org_data['minute'])
        hour_count = sum(count for _, count in org_data['hour'])
        
        # Check limits
        if minute_count >= requests_per_minute:
            return False, f"Rate limit exceeded: {requests_per_minute} requests per minute"
        if hour_count >= requests_per_hour:
            return False, f"Rate limit exceeded: {requests_per_hour} requests per hour"
        
        # Record the request
        org_data['minute'].append((current_time, 1))
        org_data['hour'].append((current_time, 1))
        
        return True, ""


# Global rate limit tracker
rate_limiter = RateLimitTracker()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce per-organization rate limits."""
    
    async def dispatch(self, request: Request, call_next):
        # Extract org_id from headers (X-Org-ID) or use 'default'
        org_id = request.headers.get("X-Org-ID", "default")
        
        # Get org configuration
        org_config = config_store.get_org_config(org_id)
        
        if not org_config.enabled:
            return JSONResponse(
                status_code=403,
                content={"error": "Organization is disabled"}
            )
        
        # Check rate limits
        is_allowed, reason = rate_limiter.check_rate_limit(
            org_id,
            org_config.rate_limit.requests_per_minute,
            org_config.rate_limit.requests_per_hour
        )
        
        if not is_allowed:
            return JSONResponse(
                status_code=429,
                content={"error": reason, "org_id": org_id}
            )
        
        # Continue with the request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Org"] = org_id
        response.headers["X-RateLimit-Minute"] = str(org_config.rate_limit.requests_per_minute)
        response.headers["X-RateLimit-Hour"] = str(org_config.rate_limit.requests_per_hour)
        
        return response
