"""Cost tracking for jobs with configurable limits."""

from typing import Dict, Optional
from .config import config
from .logger import get_logger


logger = get_logger(__name__)


class CostExceededError(Exception):
    """Raised when job cost exceeds the maximum allowed cost."""
    pass


class CostTracker:
    """Track estimated costs per job and enforce limits."""
    
    # Approximate pricing per 1K tokens (can be configured per model)
    DEFAULT_PRICING = {
        'gpt-4': {'input': 0.03, 'output': 0.06},
        'gpt-4-turbo': {'input': 0.01, 'output': 0.03},
        'gpt-3.5-turbo': {'input': 0.0005, 'output': 0.0015},
        'claude-3-opus': {'input': 0.015, 'output': 0.075},
        'claude-3-sonnet': {'input': 0.003, 'output': 0.015},
        'claude-3-haiku': {'input': 0.00025, 'output': 0.00125},
    }
    
    def __init__(self, job_id: str, max_cost: Optional[float] = None):
        """
        Initialize cost tracker for a job.
        
        Args:
            job_id: Unique identifier for the job
            max_cost: Maximum allowed cost (defaults to config.MAX_JOB_COST)
        """
        self.job_id = job_id
        self.max_cost = max_cost if max_cost is not None else config.MAX_JOB_COST
        self.total_cost = 0.0
        self.usage_by_model: Dict[str, Dict[str, int]] = {}
        
        logger.info("cost_tracker_initialized", job_id=job_id, max_cost=self.max_cost)
    
    def estimate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        pricing: Optional[Dict[str, Dict[str, float]]] = None
    ) -> float:
        """
        Estimate cost for a model request.
        
        Args:
            model: Model identifier
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            pricing: Optional custom pricing dict
            
        Returns:
            Estimated cost in USD
        """
        pricing_data = pricing or self.DEFAULT_PRICING
        
        # Use default pricing if model not found
        if model not in pricing_data:
            logger.warning("model_pricing_not_found", model=model, using_default=True)
            model_pricing = pricing_data.get('gpt-3.5-turbo', {'input': 0.001, 'output': 0.002})
        else:
            model_pricing = pricing_data[model]
        
        input_cost = (input_tokens / 1000.0) * model_pricing['input']
        output_cost = (output_tokens / 1000.0) * model_pricing['output']
        
        return input_cost + output_cost
    
    def track_usage(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        pricing: Optional[Dict[str, Dict[str, float]]] = None
    ) -> float:
        """
        Track usage and update total cost.
        
        Args:
            model: Model identifier
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            pricing: Optional custom pricing dict
            
        Returns:
            Cost of this request
            
        Raises:
            CostExceededError: If total cost exceeds max_cost
        """
        cost = self.estimate_cost(model, input_tokens, output_tokens, pricing)
        self.total_cost += cost
        
        # Track usage by model
        if model not in self.usage_by_model:
            self.usage_by_model[model] = {'input_tokens': 0, 'output_tokens': 0, 'cost': 0.0}
        
        self.usage_by_model[model]['input_tokens'] += input_tokens
        self.usage_by_model[model]['output_tokens'] += output_tokens
        self.usage_by_model[model]['cost'] += cost
        
        logger.info(
            "usage_tracked",
            job_id=self.job_id,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            total_cost=self.total_cost
        )
        
        # Check if we've exceeded the limit
        if self.total_cost > self.max_cost:
            logger.error(
                "cost_limit_exceeded",
                job_id=self.job_id,
                total_cost=self.total_cost,
                max_cost=self.max_cost
            )
            raise CostExceededError(
                f"Job {self.job_id} exceeded max cost: ${self.total_cost:.4f} > ${self.max_cost:.4f}"
            )
        
        return cost
    
    def get_summary(self) -> Dict:
        """Get a summary of costs and usage."""
        return {
            'job_id': self.job_id,
            'total_cost': self.total_cost,
            'max_cost': self.max_cost,
            'remaining_budget': self.max_cost - self.total_cost,
            'usage_by_model': self.usage_by_model
        }
