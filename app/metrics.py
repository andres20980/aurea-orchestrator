"""Prometheus metrics for aurea-orchestrator."""
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
from app.cache import cache_manager


# Cache metrics
cache_hits = Counter(
    "cache_hits_total",
    "Total number of cache hits",
    ["cache_type"]
)

cache_misses = Counter(
    "cache_misses_total",
    "Total number of cache misses",
    ["cache_type"]
)

cache_hit_rate = Gauge(
    "cache_hit_rate",
    "Cache hit rate percentage",
)


def update_cache_metrics():
    """Update Prometheus metrics from cache statistics."""
    stats = cache_manager.get_stats()
    
    # Update counters (set to current values)
    cache_hits.labels(cache_type="llm")._value._value = stats["llm"]["hits"]
    cache_hits.labels(cache_type="embedding")._value._value = stats["embedding"]["hits"]
    
    cache_misses.labels(cache_type="llm")._value._value = stats["llm"]["misses"]
    cache_misses.labels(cache_type="embedding")._value._value = stats["embedding"]["misses"]
    
    # Update hit rate gauge
    cache_hit_rate.set(stats["total"]["hit_rate"])


def get_metrics() -> bytes:
    """Get Prometheus metrics.
    
    Returns:
        Metrics in Prometheus format
    """
    update_cache_metrics()
    return generate_latest()
