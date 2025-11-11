"""Tests for cache functionality."""
import pytest
import fakeredis.aioredis
from app.cache import CacheManager, cache_llm_response, cache_embedding
from app.config import settings


@pytest.mark.asyncio
async def test_cache_manager_connection():
    """Test cache manager connection."""
    manager = CacheManager()
    manager._redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
    # Connection is already established with fake redis
    await manager._redis.aclose()


@pytest.mark.asyncio
async def test_cache_get_set():
    """Test basic cache get/set operations."""
    manager = CacheManager()
    manager._redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
    
    # Set a value
    await manager.set("test_key", "test_value", 60)
    
    # Get the value
    value = await manager.get("test_key")
    assert value == "test_value"
    
    await manager._redis.aclose()


@pytest.mark.asyncio
async def test_cache_delete():
    """Test cache deletion."""
    manager = CacheManager()
    manager._redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
    
    # Set multiple values
    await manager.set("test_key1", "value1", 60)
    await manager.set("test_key2", "value2", 60)
    
    # Delete all
    deleted = await manager.delete("test_key*")
    assert deleted >= 2
    
    # Verify deletion
    value = await manager.get("test_key1")
    assert value is None
    
    await manager._redis.aclose()


@pytest.mark.asyncio
async def test_cache_stats():
    """Test cache statistics."""
    manager = CacheManager()
    
    # Record some hits and misses
    manager.record_hit("llm")
    manager.record_hit("llm")
    manager.record_miss("llm")
    manager.record_hit("embedding")
    manager.record_miss("embedding")
    
    stats = manager.get_stats()
    
    assert stats["llm"]["hits"] == 2
    assert stats["llm"]["misses"] == 1
    assert stats["embedding"]["hits"] == 1
    assert stats["embedding"]["misses"] == 1
    assert stats["total"]["hits"] == 3
    assert stats["total"]["misses"] == 2
    assert stats["total"]["requests"] == 5
    assert stats["total"]["hit_rate"] == 60.0


@pytest.mark.asyncio
async def test_cache_stats_reset():
    """Test cache statistics reset."""
    manager = CacheManager()
    
    # Record some hits
    manager.record_hit("llm")
    manager.record_hit("embedding")
    
    # Reset stats
    manager.reset_stats()
    
    stats = manager.get_stats()
    assert stats["total"]["hits"] == 0
    assert stats["total"]["misses"] == 0


@pytest.mark.asyncio
async def test_llm_cache_decorator(fake_redis):
    """Test LLM caching decorator."""
    from app.cache import cache_manager
    
    # Use the global cache manager
    cache_manager._redis = fake_redis
    cache_manager.reset_stats()
    
    call_count = 0
    
    @cache_llm_response
    async def mock_llm(prompt: str, context: str = "", model: str = ""):
        nonlocal call_count
        call_count += 1
        return {"response": f"Answer to {prompt}"}
    
    # First call - should miss cache
    result1 = await mock_llm(prompt="test", context="ctx", model="gpt")
    assert call_count == 1
    assert result1["response"] == "Answer to test"
    assert cache_manager.get_stats()["llm"]["misses"] == 1
    
    # Second call with same params - should hit cache
    result2 = await mock_llm(prompt="test", context="ctx", model="gpt")
    assert call_count == 1  # Should not increment
    assert result2["response"] == "Answer to test"
    assert cache_manager.get_stats()["llm"]["hits"] == 1
    
    # Third call with different params - should miss cache
    result3 = await mock_llm(prompt="other", context="ctx", model="gpt")
    assert call_count == 2
    assert result3["response"] == "Answer to other"
    assert cache_manager.get_stats()["llm"]["misses"] == 2


@pytest.mark.asyncio
async def test_llm_cache_bypass(fake_redis):
    """Test LLM cache bypass."""
    from app.cache import cache_manager
    
    # Use the global cache manager
    cache_manager._redis = fake_redis
    cache_manager.reset_stats()
    
    call_count = 0
    
    @cache_llm_response
    async def mock_llm(prompt: str, context: str = "", model: str = "", bypass_cache: bool = False):
        nonlocal call_count
        call_count += 1
        return {"response": f"Answer {call_count}"}
    
    # First call
    result1 = await mock_llm(prompt="test", context="ctx", model="gpt")
    assert call_count == 1
    
    # Second call with bypass_cache=True
    result2 = await mock_llm(prompt="test", context="ctx", model="gpt", bypass_cache=True)
    assert call_count == 2  # Should call function again
    assert result2["response"] == "Answer 2"


@pytest.mark.asyncio
async def test_embedding_cache_decorator(fake_redis):
    """Test embedding caching decorator."""
    from app.cache import cache_manager
    
    # Use the global cache manager
    cache_manager._redis = fake_redis
    cache_manager.reset_stats()
    
    call_count = 0
    
    @cache_embedding
    async def mock_embedding(text: str, model: str = ""):
        nonlocal call_count
        call_count += 1
        return {"embedding": [0.1, 0.2, 0.3]}
    
    # First call - should miss cache
    result1 = await mock_embedding(text="hello", model="ada")
    assert call_count == 1
    assert cache_manager.get_stats()["embedding"]["misses"] == 1
    
    # Second call with same params - should hit cache
    result2 = await mock_embedding(text="hello", model="ada")
    assert call_count == 1  # Should not increment
    assert cache_manager.get_stats()["embedding"]["hits"] == 1
    
    # Third call with different params - should miss cache
    result3 = await mock_embedding(text="world", model="ada")
    assert call_count == 2
    assert cache_manager.get_stats()["embedding"]["misses"] == 2


@pytest.mark.asyncio
async def test_cache_key_generation():
    """Test cache key generation."""
    manager = CacheManager()
    
    # Same parameters should generate same key
    key1 = manager._generate_key("llm", prompt="test", context="ctx", model="gpt")
    key2 = manager._generate_key("llm", prompt="test", context="ctx", model="gpt")
    assert key1 == key2
    
    # Different parameters should generate different keys
    key3 = manager._generate_key("llm", prompt="other", context="ctx", model="gpt")
    assert key1 != key3
    
    # Different prefix should generate different keys
    key4 = manager._generate_key("embedding", prompt="test", context="ctx", model="gpt")
    assert key1 != key4
