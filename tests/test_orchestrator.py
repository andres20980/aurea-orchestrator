"""Tests for orchestrator."""

import pytest
from aurea.orchestrator import Orchestrator, ModelNotAllowedError
from aurea.cost_tracker import CostExceededError
from aurea.circuit_breaker import CircuitBreakerError
from aurea.config import Config


class TestOrchestrator:
    """Test orchestrator functionality."""
    
    def test_initialization(self):
        """Test orchestrator initialization."""
        orch = Orchestrator("job-1", max_cost=5.0)
        assert orch.job_id == "job-1"
        assert orch.cost_tracker.max_cost == 5.0
        assert orch.rate_limiter is not None
        assert orch.retry_handler is not None
    
    def test_validate_model_allowed(self):
        """Test model validation when allowed."""
        orch = Orchestrator("job-1")
        result = orch.validate_model("gpt-4")
        assert result is True
    
    def test_validate_model_denied(self):
        """Test model validation when denied."""
        config = Config(DENIED_MODELS=["bad-model"])
        # Temporarily patch global config
        import aurea.orchestrator as orch_module
        old_config = orch_module.config
        orch_module.config = config
        
        try:
            orch = Orchestrator("job-1")
            with pytest.raises(ModelNotAllowedError):
                orch.validate_model("bad-model")
        finally:
            orch_module.config = old_config
    
    def test_execute_request_success(self):
        """Test successful request execution."""
        orch = Orchestrator("job-1", max_cost=10.0)
        
        call_count = [0]
        
        def mock_request():
            call_count[0] += 1
            return {"result": "success"}
        
        result = orch.execute_request(
            model="gpt-3.5-turbo",
            input_tokens=100,
            output_tokens=50,
            request_func=mock_request
        )
        
        assert result == {"result": "success"}
        assert call_count[0] == 1
        assert orch.cost_tracker.total_cost > 0
    
    def test_execute_request_with_retry(self):
        """Test request execution with retry."""
        orch = Orchestrator("job-1", max_cost=10.0)
        
        call_count = [0]
        
        def flaky_request():
            call_count[0] += 1
            if call_count[0] < 3:
                raise ValueError("Temporary error")
            return {"result": "success"}
        
        result = orch.execute_request(
            model="gpt-3.5-turbo",
            input_tokens=100,
            output_tokens=50,
            request_func=flaky_request
        )
        
        assert result == {"result": "success"}
        assert call_count[0] == 3  # Should retry until success
    
    def test_execute_request_cost_exceeded(self):
        """Test that cost limit is enforced."""
        orch = Orchestrator("job-1", max_cost=0.001)
        
        def mock_request():
            return {"result": "success"}
        
        with pytest.raises(CostExceededError):
            orch.execute_request(
                model="gpt-4",
                input_tokens=100000,
                output_tokens=50000,
                request_func=mock_request
            )
    
    def test_get_status(self):
        """Test getting orchestrator status."""
        orch = Orchestrator("job-1", max_cost=10.0)
        
        def mock_request():
            return {"result": "success"}
        
        orch.execute_request(
            model="gpt-3.5-turbo",
            input_tokens=100,
            output_tokens=50,
            request_func=mock_request
        )
        
        status = orch.get_status()
        assert status["job_id"] == "job-1"
        assert "cost_summary" in status
        assert status["cost_summary"]["total_cost"] > 0
    
    def test_circuit_breaker_integration(self):
        """Test circuit breaker integration."""
        orch = Orchestrator("job-1", max_cost=10.0)
        
        # Lower the retry count for faster test
        orch.retry_handler.max_retries = 1
        
        def always_fail():
            raise ValueError("Persistent error")
        
        # Keep failing until circuit opens
        # Each request will retry once, so we need multiple iterations
        from aurea.retry_handler import RetryExhaustedError
        for _ in range(3):
            try:
                orch.execute_request(
                    model="test-model",
                    input_tokens=100,
                    output_tokens=50,
                    request_func=always_fail
                )
            except (ValueError, CircuitBreakerError, RetryExhaustedError):
                pass
        
        # Circuit should be open for this model
        assert "test-model" in orch.circuit_breakers
        # Circuit should have accumulated failures
        assert orch.circuit_breakers["test-model"].failure_count > 0
    
    def test_reset(self):
        """Test orchestrator reset."""
        orch = Orchestrator("job-1", max_cost=10.0)
        
        # Create a circuit breaker by making some requests
        def mock_request():
            return {"result": "success"}
        
        orch.execute_request(
            model="gpt-3.5-turbo",
            input_tokens=100,
            output_tokens=50,
            request_func=mock_request
        )
        
        orch.reset()
        
        # Circuit breakers should be reset
        for breaker in orch.circuit_breakers.values():
            assert breaker.failure_count == 0
