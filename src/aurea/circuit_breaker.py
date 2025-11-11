"""Circuit breaker for handling repeated failures."""

import time
from enum import Enum
from typing import Callable, TypeVar, Optional
from .config import config
from .logger import get_logger


logger = get_logger(__name__)

T = TypeVar('T')


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failures detected, requests blocked
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreakerError(Exception):
    """Raised when circuit is open."""
    pass


class CircuitBreaker:
    """Circuit breaker for handling repeated failures."""
    
    def __init__(
        self,
        name: str,
        failure_threshold: Optional[int] = None,
        timeout: Optional[float] = None
    ):
        """
        Initialize circuit breaker.
        
        Args:
            name: Identifier for this circuit
            failure_threshold: Number of failures before opening circuit
            timeout: Time in seconds before attempting to close circuit
        """
        self.name = name
        self.failure_threshold = (
            failure_threshold if failure_threshold is not None
            else config.CIRCUIT_BREAKER_THRESHOLD
        )
        self.timeout = timeout if timeout is not None else config.CIRCUIT_BREAKER_TIMEOUT
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.opened_at: Optional[float] = None
        
        logger.info(
            "circuit_breaker_initialized",
            name=name,
            failure_threshold=self.failure_threshold,
            timeout=self.timeout
        )
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.opened_at is None:
            return False
        return (time.time() - self.opened_at) >= self.timeout
    
    def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """
        Execute function through circuit breaker.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Result from func
            
        Raises:
            CircuitBreakerError: If circuit is open
            Exception: Any exception from func
        """
        # Check circuit state
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                logger.info("circuit_breaker_half_open", name=self.name)
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
            else:
                logger.warning("circuit_breaker_open", name=self.name)
                raise CircuitBreakerError(
                    f"Circuit breaker '{self.name}' is open. "
                    f"Too many failures ({self.failure_count})"
                )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
            
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """Handle successful call."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            
            # Reset circuit after successful test
            logger.info(
                "circuit_breaker_reset",
                name=self.name,
                success_count=self.success_count
            )
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.opened_at = None
        
        # Reset failure count on success in closed state
        if self.state == CircuitState.CLOSED:
            self.failure_count = 0
    
    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        logger.warning(
            "circuit_breaker_failure",
            name=self.name,
            failure_count=self.failure_count,
            threshold=self.failure_threshold,
            state=self.state.value
        )
        
        if self.state == CircuitState.HALF_OPEN:
            # Failed during test, reopen circuit
            logger.error("circuit_breaker_reopened", name=self.name)
            self.state = CircuitState.OPEN
            self.opened_at = time.time()
            
        elif self.failure_count >= self.failure_threshold:
            # Threshold exceeded, open circuit
            logger.error(
                "circuit_breaker_opened",
                name=self.name,
                failure_count=self.failure_count,
                threshold=self.failure_threshold
            )
            self.state = CircuitState.OPEN
            self.opened_at = time.time()
    
    def reset(self):
        """Manually reset the circuit breaker."""
        logger.info("circuit_breaker_manual_reset", name=self.name)
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.opened_at = None
        self.last_failure_time = None
    
    def get_state(self) -> dict:
        """Get current state information."""
        return {
            'name': self.name,
            'state': self.state.value,
            'failure_count': self.failure_count,
            'success_count': self.success_count,
            'failure_threshold': self.failure_threshold,
            'timeout': self.timeout,
            'opened_at': self.opened_at,
            'last_failure_time': self.last_failure_time
        }


def with_circuit_breaker(
    name: str,
    failure_threshold: Optional[int] = None,
    timeout: Optional[float] = None
):
    """
    Decorator for automatic circuit breaker protection.
    
    Args:
        name: Circuit breaker identifier
        failure_threshold: Number of failures before opening
        timeout: Time before attempting reset
    """
    breaker = CircuitBreaker(name, failure_threshold, timeout)
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args, **kwargs) -> T:
            return breaker.call(func, *args, **kwargs)
        wrapper.circuit_breaker = breaker  # Allow access to breaker
        return wrapper
    return decorator
