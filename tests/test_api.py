"""Tests for API endpoints."""
import pytest
from app.config import settings


@pytest.mark.asyncio
async def test_root_endpoint(client):
    """Test root endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == settings.app_name
    assert "cache_enabled" in data


@pytest.mark.asyncio
async def test_health_endpoint(client):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_cache_stats_without_auth(client):
    """Test cache stats endpoint without authentication."""
    # When no API key is configured, should allow access
    response = await client.get("/cache/stats")
    if settings.api_key:
        assert response.status_code == 401
    else:
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_cache_stats_with_auth(client, api_key):
    """Test cache stats endpoint with authentication."""
    response = await client.get(
        "/cache/stats",
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 200
    data = response.json()
    assert "llm" in data
    assert "embedding" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_cache_clear_without_auth(client):
    """Test cache clear endpoint without authentication."""
    response = await client.post("/cache/clear")
    if settings.api_key:
        assert response.status_code == 401
    else:
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_cache_clear_with_auth(client, api_key):
    """Test cache clear endpoint with authentication."""
    response = await client.post(
        "/cache/clear",
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "deleted_keys" in data


@pytest.mark.asyncio
async def test_llm_generate_endpoint(client):
    """Test LLM generate endpoint."""
    # First call
    response1 = await client.post(
        "/llm/generate",
        params={
            "prompt": "test prompt",
            "context": "test context",
            "model": "gpt-4"
        }
    )
    assert response1.status_code == 200
    data1 = response1.json()
    assert "response" in data1
    
    # Second call with same params (should hit cache)
    response2 = await client.post(
        "/llm/generate",
        params={
            "prompt": "test prompt",
            "context": "test context",
            "model": "gpt-4"
        }
    )
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2 == data1


@pytest.mark.asyncio
async def test_llm_generate_bypass_cache(client):
    """Test LLM generate endpoint with cache bypass."""
    response = await client.post(
        "/llm/generate",
        params={
            "prompt": "test",
            "bypass_cache": True
        }
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_embedding_generate_endpoint(client):
    """Test embedding generate endpoint."""
    # First call
    response1 = await client.post(
        "/embedding/generate",
        params={
            "text": "test text",
            "model": "ada-002"
        }
    )
    assert response1.status_code == 200
    data1 = response1.json()
    assert "embedding" in data1
    
    # Second call with same params (should hit cache)
    response2 = await client.post(
        "/embedding/generate",
        params={
            "text": "test text",
            "model": "ada-002"
        }
    )
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2 == data1


@pytest.mark.asyncio
async def test_embedding_generate_bypass_cache(client):
    """Test embedding generate endpoint with cache bypass."""
    response = await client.post(
        "/embedding/generate",
        params={
            "text": "test",
            "bypass_cache": True
        }
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_metrics_endpoint(client):
    """Test Prometheus metrics endpoint."""
    response = await client.get("/metrics")
    assert response.status_code == 200
    assert "cache_hits_total" in response.text
    assert "cache_misses_total" in response.text
    assert "cache_hit_rate" in response.text


@pytest.mark.asyncio
async def test_cache_hit_statistics(client, api_key):
    """Test that cache statistics are tracked correctly."""
    # Make a few requests
    await client.post("/llm/generate", params={"prompt": "test1"})
    await client.post("/llm/generate", params={"prompt": "test1"})  # Cache hit
    await client.post("/embedding/generate", params={"text": "embed1"})
    await client.post("/embedding/generate", params={"text": "embed1"})  # Cache hit
    
    # Check stats
    response = await client.get(
        "/cache/stats",
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 200
    stats = response.json()
    
    assert stats["llm"]["hits"] >= 1
    assert stats["llm"]["misses"] >= 1
    assert stats["embedding"]["hits"] >= 1
    assert stats["embedding"]["misses"] >= 1
