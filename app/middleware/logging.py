"""Request logging middleware."""
import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("api_gateway")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all incoming requests."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Extract request information
        org_id = request.headers.get("X-Org-ID", "default")
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path
        
        # Log request
        logger.info(
            f"Request started: {method} {path} | "
            f"Org: {org_id} | IP: {client_ip}"
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            logger.info(
                f"Request completed: {method} {path} | "
                f"Status: {response.status_code} | "
                f"Duration: {duration:.3f}s | "
                f"Org: {org_id} | IP: {client_ip}"
            )
            
            return response
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Request failed: {method} {path} | "
                f"Error: {str(e)} | "
                f"Duration: {duration:.3f}s | "
                f"Org: {org_id} | IP: {client_ip}"
            )
            raise
