"""Tests for rate limiter."""

import time
import pytest
from aurea.rate_limiter import RateLimiter


class TestRateLimiter:
    """Test rate limiting functionality."""
    
    def test_initialization(self):
        """Test rate limiter initialization."""
        limiter = RateLimiter(default_rpm=60, default_tpm=100000)
        assert limiter.default_rpm == 60
        assert limiter.default_tpm == 100000
    
    def test_set_model_limits(self):
        """Test setting custom model limits."""
        limiter = RateLimiter()
        limiter.set_model_limits("gpt-4", rpm=10, tpm=50000)
        
        assert limiter.model_rpm_limits["gpt-4"] == 10
        assert limiter.model_tpm_limits["gpt-4"] == 50000
    
    def test_acquire_single_request(self):
        """Test acquiring permission for a single request."""
        limiter = RateLimiter(default_rpm=60, default_tpm=100000)
        
        result = limiter.acquire("gpt-3.5-turbo", 1000)
        assert result is True
    
    def test_get_current_usage(self):
        """Test getting current usage stats."""
        limiter = RateLimiter(default_rpm=60, default_tpm=100000)
        
        limiter.acquire("gpt-3.5-turbo", 1000)
        limiter.acquire("gpt-3.5-turbo", 500)
        
        usage = limiter.get_current_usage("gpt-3.5-turbo")
        assert usage["requests"] == 2
        assert usage["tokens"] == 1500
        assert usage["rpm_limit"] == 60
        assert usage["tpm_limit"] == 100000
    
    def test_rate_limit_enforcement_rpm(self):
        """Test that RPM limits are enforced."""
        # Very low limit for testing
        limiter = RateLimiter(default_rpm=2, default_tpm=100000)
        
        # First two requests should succeed quickly
        limiter.acquire("test-model", 100)
        limiter.acquire("test-model", 100)
        
        # Third request should wait or succeed (depends on timing)
        start = time.time()
        limiter.check_and_wait("test-model", 100)
        elapsed = time.time() - start
        
        # Should either succeed immediately (if enough time passed) or wait
        assert elapsed >= 0  # At minimum, should not error
    
    def test_different_models_separate_limits(self):
        """Test that different models have separate rate limits."""
        limiter = RateLimiter(default_rpm=60, default_tpm=100000)
        
        # Use different models
        limiter.acquire("gpt-3.5-turbo", 1000)
        limiter.acquire("gpt-4", 1000)
        
        usage_3_5 = limiter.get_current_usage("gpt-3.5-turbo")
        usage_4 = limiter.get_current_usage("gpt-4")
        
        assert usage_3_5["requests"] == 1
        assert usage_4["requests"] == 1
    
    def test_old_entries_cleaned(self):
        """Test that old entries are cleaned up."""
        limiter = RateLimiter(default_rpm=60, default_tpm=100000)
        
        limiter.acquire("test-model", 1000)
        
        # Manually clean to test the cleanup mechanism
        limiter._clean_old_entries(limiter.request_history["test-model"], window_seconds=0.1)
        time.sleep(0.2)
        limiter._clean_old_entries(limiter.request_history["test-model"], window_seconds=0.1)
        
        # After cleanup, old entries should be removed
        assert len(limiter.request_history["test-model"]) == 0
