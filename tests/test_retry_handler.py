"""Tests for retry handler."""

import pytest
from aurea.retry_handler import RetryHandler, RetryExhaustedError


class TestRetryHandler:
    """Test retry handler functionality."""
    
    def test_initialization(self):
        """Test retry handler initialization."""
        handler = RetryHandler(max_retries=3, base_delay=1.0, max_delay=60.0)
        assert handler.max_retries == 3
        assert handler.base_delay == 1.0
        assert handler.max_delay == 60.0
    
    def test_calculate_delay(self):
        """Test delay calculation with exponential backoff."""
        handler = RetryHandler(max_retries=3, base_delay=1.0, max_delay=60.0)
        
        # First retry
        delay_0 = handler.calculate_delay(0)
        assert 0.75 <= delay_0 <= 1.25  # base_delay * 1 with jitter
        
        # Second retry
        delay_1 = handler.calculate_delay(1)
        assert 1.5 <= delay_1 <= 2.5  # base_delay * 2 with jitter
        
        # Third retry
        delay_2 = handler.calculate_delay(2)
        assert 3.0 <= delay_2 <= 5.0  # base_delay * 4 with jitter
    
    def test_successful_first_try(self):
        """Test function succeeds on first try."""
        handler = RetryHandler(max_retries=3, base_delay=0.1)
        
        call_count = [0]
        
        def success_func():
            call_count[0] += 1
            return "success"
        
        result = handler.retry(success_func)
        assert result == "success"
        assert call_count[0] == 1
    
    def test_successful_after_retries(self):
        """Test function succeeds after some retries."""
        handler = RetryHandler(max_retries=3, base_delay=0.1)
        
        call_count = [0]
        
        def flaky_func():
            call_count[0] += 1
            if call_count[0] < 3:
                raise ValueError("Temporary error")
            return "success"
        
        result = handler.retry(flaky_func)
        assert result == "success"
        assert call_count[0] == 3
    
    def test_retry_exhausted(self):
        """Test that retries are exhausted on persistent failure."""
        handler = RetryHandler(max_retries=3, base_delay=0.01, max_delay=0.1)
        
        call_count = [0]
        
        def fail_func():
            call_count[0] += 1
            raise ValueError("Persistent error")
        
        with pytest.raises(RetryExhaustedError):
            handler.retry(fail_func)
        
        # Should try initial + 3 retries = 4 total
        assert call_count[0] == 4
    
    def test_non_retryable_exception(self):
        """Test that non-retryable exceptions are raised immediately."""
        handler = RetryHandler(max_retries=3, base_delay=0.1)
        
        call_count = [0]
        
        def fail_func():
            call_count[0] += 1
            raise KeyError("Non-retryable")
        
        with pytest.raises(KeyError):
            handler.retry(fail_func, retryable_exceptions=(ValueError,))
        
        # Should only try once
        assert call_count[0] == 1
    
    def test_max_delay_cap(self):
        """Test that delay is capped at max_delay."""
        handler = RetryHandler(max_retries=10, base_delay=1.0, max_delay=5.0)
        
        # Large attempt number should still cap at max_delay
        delay = handler.calculate_delay(10)
        assert delay <= 5.0 * 1.25  # max_delay + jitter
