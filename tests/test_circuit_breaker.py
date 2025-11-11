"""Tests for circuit breaker."""

import pytest
from aurea.circuit_breaker import CircuitBreaker, CircuitState, CircuitBreakerError


class TestCircuitBreaker:
    """Test circuit breaker functionality."""
    
    def test_initialization(self):
        """Test circuit breaker initialization."""
        breaker = CircuitBreaker("test", failure_threshold=3, timeout=60.0)
        assert breaker.name == "test"
        assert breaker.failure_threshold == 3
        assert breaker.timeout == 60.0
        assert breaker.state == CircuitState.CLOSED
    
    def test_successful_call(self):
        """Test successful function call."""
        breaker = CircuitBreaker("test", failure_threshold=3)
        
        def success_func():
            return "success"
        
        result = breaker.call(success_func)
        assert result == "success"
        assert breaker.failure_count == 0
    
    def test_failed_call(self):
        """Test failed function call."""
        breaker = CircuitBreaker("test", failure_threshold=3)
        
        def fail_func():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            breaker.call(fail_func)
        
        assert breaker.failure_count == 1
        assert breaker.state == CircuitState.CLOSED
    
    def test_circuit_opens_after_threshold(self):
        """Test that circuit opens after threshold failures."""
        breaker = CircuitBreaker("test", failure_threshold=3)
        
        def fail_func():
            raise ValueError("Test error")
        
        # First 3 failures should increment count but not open
        for i in range(3):
            with pytest.raises(ValueError):
                breaker.call(fail_func)
        
        assert breaker.state == CircuitState.OPEN
        
        # Next call should raise CircuitBreakerError
        with pytest.raises(CircuitBreakerError):
            breaker.call(fail_func)
    
    def test_circuit_half_open_after_timeout(self):
        """Test that circuit moves to half-open after timeout."""
        breaker = CircuitBreaker("test", failure_threshold=2, timeout=0.1)
        
        def fail_func():
            raise ValueError("Test error")
        
        # Open the circuit
        for i in range(2):
            with pytest.raises(ValueError):
                breaker.call(fail_func)
        
        assert breaker.state == CircuitState.OPEN
        
        # Wait for timeout
        import time
        time.sleep(0.2)
        
        # Should transition to half-open
        def success_func():
            return "success"
        
        result = breaker.call(success_func)
        assert result == "success"
        assert breaker.state == CircuitState.CLOSED
    
    def test_manual_reset(self):
        """Test manual circuit reset."""
        breaker = CircuitBreaker("test", failure_threshold=2)
        
        def fail_func():
            raise ValueError("Test error")
        
        # Open the circuit
        for i in range(2):
            with pytest.raises(ValueError):
                breaker.call(fail_func)
        
        assert breaker.state == CircuitState.OPEN
        
        # Manual reset
        breaker.reset()
        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0
    
    def test_get_state(self):
        """Test getting circuit state information."""
        breaker = CircuitBreaker("test", failure_threshold=3)
        
        state = breaker.get_state()
        assert state["name"] == "test"
        assert state["state"] == CircuitState.CLOSED.value
        assert state["failure_count"] == 0
        assert state["failure_threshold"] == 3
