"""Main FastAPI application for aurea-orchestrator."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Response
from fastapi.responses import PlainTextResponse
from app.config import settings
from app.cache import cache_manager, cache_llm_response, cache_embedding
from app.auth import verify_api_key
from app.metrics import get_metrics, CONTENT_TYPE_LATEST

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup
    logger.info("Starting aurea-orchestrator")
    await cache_manager.connect()
    yield
    # Shutdown
    logger.info("Shutting down aurea-orchestrator")
    await cache_manager.disconnect()


app = FastAPI(
    title=settings.app_name,
    description="Automated Unified Reasoning & Execution Agents with Redis caching",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "cache_enabled": settings.cache_enabled,
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/cache/stats")
async def cache_stats(api_key: str = Depends(verify_api_key)):
    """Get cache statistics.
    
    Requires API key authentication.
    
    Returns:
        Cache statistics including hits, misses, and hit rate
    """
    return cache_manager.get_stats()


@app.post("/cache/clear")
async def cache_clear(api_key: str = Depends(verify_api_key)):
    """Clear all cache entries.
    
    Requires API key authentication.
    
    Returns:
        Number of cache entries cleared
    """
    deleted = await cache_manager.delete()
    cache_manager.reset_stats()
    return {
        "message": "Cache cleared successfully",
        "deleted_keys": deleted,
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint.
    
    Returns:
        Metrics in Prometheus format
    """
    metrics_data = get_metrics()
    return Response(content=metrics_data, media_type=CONTENT_TYPE_LATEST)


# Example LLM endpoint with caching
@app.post("/llm/generate")
@cache_llm_response
async def llm_generate(
    prompt: str,
    context: str = "",
    model: str = "default",
    bypass_cache: bool = False,
):
    """Generate LLM response with caching.
    
    This is an example endpoint demonstrating the caching decorator.
    In a real implementation, this would call an actual LLM API.
    
    Args:
        prompt: The prompt text
        context: Additional context
        model: Model name
        bypass_cache: Whether to bypass cache
    
    Returns:
        LLM response
    """
    # Simulate LLM response
    logger.info(f"Generating LLM response for prompt: {prompt[:50]}...")
    return {
        "response": f"Simulated response for: {prompt}",
        "model": model,
        "cached": False,
    }


# Example embedding endpoint with caching
@app.post("/embedding/generate")
@cache_embedding
async def embedding_generate(
    text: str,
    model: str = "default",
    bypass_cache: bool = False,
):
    """Generate embedding with caching.
    
    This is an example endpoint demonstrating the caching decorator.
    In a real implementation, this would call an actual embedding API.
    
    Args:
        text: The text to embed
        model: Model name
        bypass_cache: Whether to bypass cache
    
    Returns:
        Embedding vector
    """
    # Simulate embedding response
    logger.info(f"Generating embedding for text: {text[:50]}...")
    return {
        "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],  # Simulated embedding
        "model": model,
        "cached": False,
    }
