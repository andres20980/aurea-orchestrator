"""Main orchestrator for managing jobs with cost, rate limiting, and reliability features."""

from typing import Dict, Optional, Callable, Any
from .config import config
from .cost_tracker import CostTracker, CostExceededError
from .rate_limiter import RateLimiter, RateLimitExceededError
from .circuit_breaker import CircuitBreaker, CircuitBreakerError
from .retry_handler import RetryHandler, RetryExhaustedError
from .logger import get_logger


logger = get_logger(__name__)


class ModelNotAllowedError(Exception):
    """Raised when attempting to use a denied model."""
    pass


class Orchestrator:
    """
    Main orchestrator for managing AI model jobs.
    
    Features:
    - Cost tracking with configurable limits
    - Per-model rate limiting (RPM/TPM)
    - Retry with exponential backoff
    - Circuit breaker for repeated failures
    - Model allow/deny lists
    """
    
    def __init__(
        self,
        job_id: str,
        max_cost: Optional[float] = None
    ):
        """
        Initialize orchestrator for a job.
        
        Args:
            job_id: Unique identifier for this job
            max_cost: Maximum cost for this job (defaults to config)
        """
        self.job_id = job_id
        self.cost_tracker = CostTracker(job_id, max_cost)
        self.rate_limiter = RateLimiter()
        self.retry_handler = RetryHandler()
        
        # Circuit breakers per model
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        logger.info("orchestrator_initialized", job_id=job_id, max_cost=max_cost)
    
    def _get_circuit_breaker(self, model: str) -> CircuitBreaker:
        """Get or create circuit breaker for a model."""
        if model not in self.circuit_breakers:
            self.circuit_breakers[model] = CircuitBreaker(f"{self.job_id}:{model}")
        return self.circuit_breakers[model]
    
    def validate_model(self, model: str) -> bool:
        """
        Validate that a model is allowed.
        
        Args:
            model: Model identifier
            
        Returns:
            True if model is allowed
            
        Raises:
            ModelNotAllowedError: If model is not allowed
        """
        if not config.is_model_allowed(model):
            logger.error("model_not_allowed", model=model, job_id=self.job_id)
            raise ModelNotAllowedError(
                f"Model '{model}' is not allowed. Check ALLOWED_MODELS/DENIED_MODELS configuration."
            )
        return True
    
    def execute_request(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        request_func: Callable[..., Any],
        *args,
        **kwargs
    ) -> Any:
        """
        Execute a model request with all safety features.
        
        This method:
        1. Validates the model is allowed
        2. Checks cost limits
        3. Enforces rate limits
        4. Uses circuit breaker
        5. Retries on failure with exponential backoff
        
        Args:
            model: Model identifier
            input_tokens: Expected input tokens
            output_tokens: Expected output tokens
            request_func: Function to execute the actual request
            *args: Arguments for request_func
            **kwargs: Keyword arguments for request_func
            
        Returns:
            Result from request_func
            
        Raises:
            ModelNotAllowedError: If model is denied
            CostExceededError: If cost limit exceeded
            CircuitBreakerError: If circuit is open
            RetryExhaustedError: If all retries fail
        """
        # Validate model is allowed
        self.validate_model(model)
        
        # Check cost before request
        estimated_cost = self.cost_tracker.estimate_cost(model, input_tokens, output_tokens)
        if self.cost_tracker.total_cost + estimated_cost > self.cost_tracker.max_cost:
            logger.error(
                "cost_would_exceed_limit",
                job_id=self.job_id,
                model=model,
                current_cost=self.cost_tracker.total_cost,
                estimated_cost=estimated_cost,
                max_cost=self.cost_tracker.max_cost
            )
            raise CostExceededError(
                f"Request would exceed cost limit: "
                f"${self.cost_tracker.total_cost + estimated_cost:.4f} > "
                f"${self.cost_tracker.max_cost:.4f}"
            )
        
        # Apply rate limiting
        self.rate_limiter.check_and_wait(model, input_tokens + output_tokens)
        
        # Get circuit breaker for this model
        circuit_breaker = self._get_circuit_breaker(model)
        
        # Execute with retry and circuit breaker
        def protected_request():
            return circuit_breaker.call(request_func, *args, **kwargs)
        
        try:
            result = self.retry_handler.retry(protected_request)
            
            # Track actual usage
            self.cost_tracker.track_usage(model, input_tokens, output_tokens)
            
            logger.info(
                "request_successful",
                job_id=self.job_id,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "request_failed",
                job_id=self.job_id,
                model=model,
                error=str(e),
                error_type=type(e).__name__
            )
            raise
    
    def get_status(self) -> Dict:
        """Get comprehensive status of the orchestrator."""
        return {
            'job_id': self.job_id,
            'cost_summary': self.cost_tracker.get_summary(),
            'circuit_breakers': {
                model: breaker.get_state()
                for model, breaker in self.circuit_breakers.items()
            }
        }
    
    def reset(self):
        """Reset all circuit breakers."""
        for breaker in self.circuit_breakers.values():
            breaker.reset()
        logger.info("orchestrator_reset", job_id=self.job_id)
