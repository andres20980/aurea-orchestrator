"""Redis cache manager for aurea-orchestrator."""
import hashlib
import json
import logging
from typing import Any, Optional, Callable
from functools import wraps
import redis.asyncio as redis
from app.config import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages Redis cache connections and operations."""
    
    def __init__(self):
        self._redis: Optional[redis.Redis] = None
        self._stats = {
            "llm_hits": 0,
            "llm_misses": 0,
            "embedding_hits": 0,
            "embedding_misses": 0,
        }
    
    async def connect(self):
        """Establish connection to Redis."""
        if not settings.cache_enabled:
            logger.info("Cache is disabled")
            return
        
        try:
            self._redis = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password,
                ssl=settings.redis_ssl,
                decode_responses=True,
            )
            await self._redis.ping()
            logger.info(f"Connected to Redis at {settings.redis_host}:{settings.redis_port}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._redis = None
    
    async def disconnect(self):
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            logger.info("Disconnected from Redis")
    
    def _generate_key(self, prefix: str, **kwargs) -> str:
        """Generate a cache key from the given parameters.
        
        Args:
            prefix: Key prefix (e.g., "llm", "embedding")
            **kwargs: Parameters to hash
        
        Returns:
            Cache key string
        """
        # Sort kwargs for consistent hashing
        sorted_items = sorted(kwargs.items())
        data = json.dumps(sorted_items, sort_keys=True)
        hash_value = hashlib.sha256(data.encode()).hexdigest()
        return f"{prefix}:{hash_value}"
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache.
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if not found
        """
        if not self._redis or not settings.cache_enabled:
            return None
        
        try:
            return await self._redis.get(key)
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: str, ttl: int):
        """Set value in cache with TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        if not self._redis or not settings.cache_enabled:
            return
        
        try:
            await self._redis.setex(key, ttl, value)
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
    
    async def delete(self, pattern: str = "*") -> int:
        """Delete keys matching the pattern.
        
        Args:
            pattern: Key pattern (default: all keys)
        
        Returns:
            Number of keys deleted
        """
        if not self._redis or not settings.cache_enabled:
            return 0
        
        try:
            keys = []
            async for key in self._redis.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                return await self._redis.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache delete error for pattern {pattern}: {e}")
            return 0
    
    def get_stats(self) -> dict:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        total_hits = self._stats["llm_hits"] + self._stats["embedding_hits"]
        total_misses = self._stats["llm_misses"] + self._stats["embedding_misses"]
        total_requests = total_hits + total_misses
        
        hit_rate = (total_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "llm": {
                "hits": self._stats["llm_hits"],
                "misses": self._stats["llm_misses"],
            },
            "embedding": {
                "hits": self._stats["embedding_hits"],
                "misses": self._stats["embedding_misses"],
            },
            "total": {
                "hits": total_hits,
                "misses": total_misses,
                "requests": total_requests,
                "hit_rate": round(hit_rate, 2),
            },
        }
    
    def reset_stats(self):
        """Reset cache statistics."""
        self._stats = {
            "llm_hits": 0,
            "llm_misses": 0,
            "embedding_hits": 0,
            "embedding_misses": 0,
        }
    
    def record_hit(self, cache_type: str):
        """Record a cache hit.
        
        Args:
            cache_type: Type of cache ("llm" or "embedding")
        """
        self._stats[f"{cache_type}_hits"] += 1
    
    def record_miss(self, cache_type: str):
        """Record a cache miss.
        
        Args:
            cache_type: Type of cache ("llm" or "embedding")
        """
        self._stats[f"{cache_type}_misses"] += 1


# Global cache manager instance
cache_manager = CacheManager()


def cache_llm_response(func: Callable) -> Callable:
    """Decorator to cache LLM responses.
    
    Caches responses based on hash(prompt + context + model).
    
    Args:
        func: Async function that returns LLM response
    
    Returns:
        Wrapped function with caching
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract caching parameters
        prompt = kwargs.get("prompt", "")
        context = kwargs.get("context", "")
        model = kwargs.get("model", "")
        bypass_cache = kwargs.get("bypass_cache", False)
        
        # Generate cache key
        cache_key = cache_manager._generate_key(
            "llm",
            prompt=prompt,
            context=context,
            model=model,
        )
        
        # Try to get from cache
        if not bypass_cache:
            cached = await cache_manager.get(cache_key)
            if cached is not None:
                cache_manager.record_hit("llm")
                logger.debug(f"LLM cache hit for key: {cache_key}")
                return json.loads(cached)
        
        # Cache miss - call the actual function
        cache_manager.record_miss("llm")
        logger.debug(f"LLM cache miss for key: {cache_key}")
        result = await func(*args, **kwargs)
        
        # Cache the result
        if not bypass_cache:
            await cache_manager.set(
                cache_key,
                json.dumps(result),
                settings.cache_llm_ttl
            )
        
        return result
    
    return wrapper


def cache_embedding(func: Callable) -> Callable:
    """Decorator to cache embedding responses.
    
    Caches embeddings based on hash(text + model).
    
    Args:
        func: Async function that returns embeddings
    
    Returns:
        Wrapped function with caching
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract caching parameters
        text = kwargs.get("text", "")
        model = kwargs.get("model", "")
        bypass_cache = kwargs.get("bypass_cache", False)
        
        # Generate cache key
        cache_key = cache_manager._generate_key(
            "embedding",
            text=text,
            model=model,
        )
        
        # Try to get from cache
        if not bypass_cache:
            cached = await cache_manager.get(cache_key)
            if cached is not None:
                cache_manager.record_hit("embedding")
                logger.debug(f"Embedding cache hit for key: {cache_key}")
                return json.loads(cached)
        
        # Cache miss - call the actual function
        cache_manager.record_miss("embedding")
        logger.debug(f"Embedding cache miss for key: {cache_key}")
        result = await func(*args, **kwargs)
        
        # Cache the result
        if not bypass_cache:
            await cache_manager.set(
                cache_key,
                json.dumps(result),
                settings.cache_embedding_ttl
            )
        
        return result
    
    return wrapper
