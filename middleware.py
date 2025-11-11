"""
Middleware for monitoring task execution metrics.
"""
import time
import functools
from models import Metric, get_session


class MonitoringMiddleware:
    """
    Middleware to track and log task execution metrics.
    """
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app."""
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        
    def _before_request(self):
        """Record start time before request."""
        from flask import g
        g.start_time = time.time()
    
    def _after_request(self, response):
        """Log metrics after request if applicable."""
        # This would be used for web requests
        # For task monitoring, use the decorator below
        return response


def monitor_task(job_id, task_name, model_used, estimate_cost_fn=None):
    """
    Decorator to monitor task execution.
    
    Args:
        job_id: The job identifier
        task_name: Name of the task being executed
        model_used: Name of the model being used
        estimate_cost_fn: Optional function to estimate cost based on tokens
                         Should accept (model_name, token_count) and return cost
    
    Example:
        @monitor_task("job_123", "text_generation", "gpt-4")
        def generate_text(prompt):
            # Your task implementation
            return result, token_count
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            # Execute the task
            result = func(*args, **kwargs)
            
            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract token count from result
            # Expected: function returns (result, token_count) or dict with 'tokens'
            token_count = 0
            if isinstance(result, tuple) and len(result) == 2:
                actual_result, token_count = result
            elif isinstance(result, dict) and 'tokens' in result:
                token_count = result['tokens']
            
            # Estimate cost
            cost_estimate = 0.0
            if estimate_cost_fn:
                cost_estimate = estimate_cost_fn(model_used, token_count)
            else:
                # Default cost estimation (example pricing)
                cost_estimate = estimate_default_cost(model_used, token_count)
            
            # Log to database
            log_metric(
                job_id=job_id,
                task_name=task_name,
                model_used=model_used,
                token_count=token_count,
                latency_ms=latency_ms,
                cost_estimate=cost_estimate
            )
            
            return result
        
        return wrapper
    return decorator


def estimate_default_cost(model_name, token_count):
    """
    Default cost estimation based on model and token count.
    Prices are per 1000 tokens (example pricing).
    """
    pricing = {
        'gpt-4': 0.03,
        'gpt-4-turbo': 0.01,
        'gpt-3.5-turbo': 0.002,
        'claude-3-opus': 0.015,
        'claude-3-sonnet': 0.003,
        'claude-3-haiku': 0.00025,
        'llama-2-70b': 0.0007,
        'llama-2-13b': 0.0002,
    }
    
    price_per_1k = pricing.get(model_name.lower(), 0.001)  # Default price
    return (token_count / 1000.0) * price_per_1k


def log_metric(job_id, task_name, model_used, token_count, latency_ms, cost_estimate):
    """
    Log a metric to the database.
    
    Args:
        job_id: Job identifier
        task_name: Name of the task
        model_used: Model name
        token_count: Number of tokens processed
        latency_ms: Latency in milliseconds
        cost_estimate: Estimated cost
    """
    session = get_session()
    try:
        metric = Metric(
            job_id=job_id,
            task_name=task_name,
            model_used=model_used,
            token_count=token_count,
            latency_ms=latency_ms,
            cost_estimate=cost_estimate
        )
        session.add(metric)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error logging metric: {e}")
        raise
    finally:
        session.close()
