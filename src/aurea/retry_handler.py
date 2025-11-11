"""Retry mechanism with exponential backoff."""

import time
import random
from typing import Callable, TypeVar, Optional, Type
from .config import config
from .logger import get_logger


logger = get_logger(__name__)

T = TypeVar('T')


class RetryExhaustedError(Exception):
    """Raised when all retry attempts are exhausted."""
    pass


class RetryHandler:
    """Handle retries with exponential backoff."""
    
    def __init__(
        self,
        max_retries: Optional[int] = None,
        base_delay: Optional[float] = None,
        max_delay: Optional[float] = None
    ):
        """
        Initialize retry handler.
        
        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay in seconds for exponential backoff
            max_delay: Maximum delay in seconds
        """
        self.max_retries = max_retries if max_retries is not None else config.MAX_RETRIES
        self.base_delay = base_delay if base_delay is not None else config.RETRY_BASE_DELAY
        self.max_delay = max_delay if max_delay is not None else config.RETRY_MAX_DELAY
        
        logger.info(
            "retry_handler_initialized",
            max_retries=self.max_retries,
            base_delay=self.base_delay,
            max_delay=self.max_delay
        )
    
    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay with exponential backoff and jitter.
        
        Args:
            attempt: Current attempt number (0-indexed)
            
        Returns:
            Delay in seconds
        """
        # Exponential backoff: base_delay * 2^attempt
        delay = self.base_delay * (2 ** attempt)
        
        # Cap at max_delay
        delay = min(delay, self.max_delay)
        
        # Add jitter (±25%)
        jitter = delay * 0.25 * (2 * random.random() - 1)
        delay += jitter
        
        return max(0, delay)
    
    def retry(
        self,
        func: Callable[..., T],
        *args,
        retryable_exceptions: Optional[tuple] = None,
        **kwargs
    ) -> T:
        """
        Execute function with retry logic.
        
        Args:
            func: Function to execute
            *args: Positional arguments for func
            retryable_exceptions: Tuple of exception types to retry on
            **kwargs: Keyword arguments for func
            
        Returns:
            Result from func
            
        Raises:
            RetryExhaustedError: If all retries are exhausted
            Exception: If non-retryable exception occurs
        """
        if retryable_exceptions is None:
            retryable_exceptions = (Exception,)
        
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                result = func(*args, **kwargs)
                
                if attempt > 0:
                    logger.info(
                        "retry_succeeded",
                        attempt=attempt,
                        max_retries=self.max_retries
                    )
                
                return result
                
            except retryable_exceptions as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    delay = self.calculate_delay(attempt)
                    
                    logger.warning(
                        "retry_attempt",
                        attempt=attempt,
                        max_retries=self.max_retries,
                        delay=delay,
                        error=str(e),
                        error_type=type(e).__name__
                    )
                    
                    time.sleep(delay)
                else:
                    logger.error(
                        "retry_exhausted",
                        attempt=attempt,
                        max_retries=self.max_retries,
                        error=str(e),
                        error_type=type(e).__name__
                    )
        
        raise RetryExhaustedError(
            f"Max retries ({self.max_retries}) exhausted. Last error: {last_exception}"
        ) from last_exception


def with_retry(
    max_retries: Optional[int] = None,
    base_delay: Optional[float] = None,
    max_delay: Optional[float] = None,
    retryable_exceptions: Optional[tuple] = None
):
    """
    Decorator for automatic retry with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        retryable_exceptions: Tuple of exception types to retry on
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args, **kwargs) -> T:
            handler = RetryHandler(max_retries, base_delay, max_delay)
            return handler.retry(func, *args, retryable_exceptions=retryable_exceptions, **kwargs)
        return wrapper
    return decorator
