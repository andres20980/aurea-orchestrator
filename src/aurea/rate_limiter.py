"""Rate limiter for per-model RPM and TPM limits."""

import time
from typing import Dict, Optional
from collections import deque
from .config import config
from .logger import get_logger


logger = get_logger(__name__)


class RateLimitExceededError(Exception):
    """Raised when rate limit is exceeded."""
    pass


class RateLimiter:
    """Per-model rate limiter with RPM and TPM tracking."""
    
    def __init__(
        self,
        default_rpm: Optional[int] = None,
        default_tpm: Optional[int] = None
    ):
        """
        Initialize rate limiter.
        
        Args:
            default_rpm: Default requests per minute limit
            default_tpm: Default tokens per minute limit
        """
        self.default_rpm = default_rpm if default_rpm is not None else config.DEFAULT_RPM
        self.default_tpm = default_tpm if default_tpm is not None else config.DEFAULT_TPM
        
        # Track requests and tokens per model
        self.request_history: Dict[str, deque] = {}
        self.token_history: Dict[str, deque] = {}
        
        # Custom limits per model
        self.model_rpm_limits: Dict[str, int] = {}
        self.model_tpm_limits: Dict[str, int] = {}
        
        logger.info(
            "rate_limiter_initialized",
            default_rpm=self.default_rpm,
            default_tpm=self.default_tpm
        )
    
    def set_model_limits(self, model: str, rpm: Optional[int] = None, tpm: Optional[int] = None):
        """Set custom rate limits for a specific model."""
        if rpm is not None:
            self.model_rpm_limits[model] = rpm
        if tpm is not None:
            self.model_tpm_limits[model] = tpm
        
        logger.info("model_limits_set", model=model, rpm=rpm, tpm=tpm)
    
    def _clean_old_entries(self, history: deque, window_seconds: float = 60.0):
        """Remove entries older than the time window."""
        cutoff = time.time() - window_seconds
        while history and history[0][0] < cutoff:
            history.popleft()
    
    def _get_model_rpm(self, model: str) -> int:
        """Get RPM limit for a model."""
        return self.model_rpm_limits.get(model, self.default_rpm)
    
    def _get_model_tpm(self, model: str) -> int:
        """Get TPM limit for a model."""
        return self.model_tpm_limits.get(model, self.default_tpm)
    
    def check_and_wait(self, model: str, tokens: int) -> float:
        """
        Check rate limits and wait if necessary.
        
        Args:
            model: Model identifier
            tokens: Number of tokens for this request
            
        Returns:
            Time waited in seconds
            
        Raises:
            RateLimitExceededError: If rate limit cannot be satisfied
        """
        if model not in self.request_history:
            self.request_history[model] = deque()
            self.token_history[model] = deque()
        
        current_time = time.time()
        rpm_limit = self._get_model_rpm(model)
        tpm_limit = self._get_model_tpm(model)
        
        # Clean old entries
        self._clean_old_entries(self.request_history[model])
        self._clean_old_entries(self.token_history[model])
        
        # Check RPM
        request_count = len(self.request_history[model])
        if request_count >= rpm_limit:
            oldest_request_time = self.request_history[model][0][0]
            wait_time = 60.0 - (current_time - oldest_request_time)
            if wait_time > 0:
                logger.warning(
                    "rpm_limit_reached",
                    model=model,
                    current_rpm=request_count,
                    limit=rpm_limit,
                    wait_time=wait_time
                )
                time.sleep(wait_time)
                current_time = time.time()
                self._clean_old_entries(self.request_history[model])
        
        # Check TPM
        total_tokens = sum(t[1] for t in self.token_history[model])
        if total_tokens + tokens > tpm_limit:
            # Need to wait for tokens to free up
            if self.token_history[model]:
                oldest_token_time = self.token_history[model][0][0]
                wait_time = 60.0 - (current_time - oldest_token_time)
                if wait_time > 0:
                    logger.warning(
                        "tpm_limit_reached",
                        model=model,
                        current_tpm=total_tokens,
                        requested=tokens,
                        limit=tpm_limit,
                        wait_time=wait_time
                    )
                    time.sleep(wait_time)
                    current_time = time.time()
                    self._clean_old_entries(self.token_history[model])
        
        # Record this request
        self.request_history[model].append((current_time, 1))
        self.token_history[model].append((current_time, tokens))
        
        return 0.0
    
    def acquire(self, model: str, tokens: int) -> bool:
        """
        Attempt to acquire rate limit permission.
        
        Args:
            model: Model identifier
            tokens: Number of tokens for this request
            
        Returns:
            True if permission granted
        """
        try:
            self.check_and_wait(model, tokens)
            return True
        except Exception as e:
            logger.error("rate_limit_acquire_failed", model=model, error=str(e))
            return False
    
    def get_current_usage(self, model: str) -> Dict[str, int]:
        """Get current usage for a model."""
        if model not in self.request_history:
            return {'requests': 0, 'tokens': 0}
        
        self._clean_old_entries(self.request_history[model])
        self._clean_old_entries(self.token_history[model])
        
        requests = len(self.request_history[model])
        tokens = sum(t[1] for t in self.token_history[model])
        
        return {
            'requests': requests,
            'tokens': tokens,
            'rpm_limit': self._get_model_rpm(model),
            'tpm_limit': self._get_model_tpm(model)
        }
