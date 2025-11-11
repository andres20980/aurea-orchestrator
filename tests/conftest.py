"""Test configuration for aurea-orchestrator."""
import pytest
import pytest_asyncio
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
import fakeredis.aioredis
from app.main import app
from app.cache import cache_manager
from app.config import settings


@pytest_asyncio.fixture
async def fake_redis():
    """Create fake Redis client."""
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)
    return fake


@pytest_asyncio.fixture(autouse=True)
async def setup_cache(fake_redis):
    """Setup and teardown cache for each test."""
    # Replace the real Redis connection with fake Redis
    cache_manager._redis = fake_redis
    cache_manager.reset_stats()
    yield
    # Teardown
    await fake_redis.flushall()
    cache_manager.reset_stats()
    await fake_redis.aclose()


@pytest_asyncio.fixture
async def client():
    """Create test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def api_key():
    """Get API key from settings."""
    return settings.api_key or "test-api-key"
