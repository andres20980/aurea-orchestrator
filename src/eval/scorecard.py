"""Scorecard implementation for measuring agent performance"""

from typing import Dict, Any, Optional
import time
from dataclasses import dataclass

from ..models.eval_models import EvalScore


@dataclass
class ScorecardMetrics:
    """Container for scorecard metrics"""
    accuracy: float = 0.0
    latency_ms: float = 0.0
    cost: float = 0.0
    passed: bool = False


class Scorecard:
    """
    Scorecard for tracking evaluation metrics:
    - Accuracy: How well the agent's output matches expected output
    - Latency: Time taken to execute the agent
    - Cost: Estimated cost in USD (based on API usage)
    """
    
    # Cost per 1K tokens (example rates, should be configurable)
    COST_PER_1K_INPUT_TOKENS = 0.0001
    COST_PER_1K_OUTPUT_TOKENS = 0.0002
    
    def __init__(self):
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
    
    def start_timer(self) -> None:
        """Start latency timer"""
        self.start_time = time.time()
    
    def stop_timer(self) -> float:
        """Stop latency timer and return elapsed time in milliseconds"""
        if self.start_time is None:
            return 0.0
        self.end_time = time.time()
        return (self.end_time - self.start_time) * 1000
    
    def calculate_accuracy(
        self, 
        expected: Dict[str, Any], 
        actual: Dict[str, Any]
    ) -> float:
        """
        Calculate accuracy score by comparing expected vs actual output.
        
        Supports different comparison modes:
        - exact: Exact match (1.0 or 0.0)
        - contains: Check if expected keys/values are in actual
        - similarity: String similarity for text outputs
        
        Returns:
            Accuracy score between 0.0 and 1.0
        """
        if not actual:
            return 0.0
        
        # Check for exact match
        if expected == actual:
            return 1.0
        
        # Check for 'contains' mode
        if "contains" in expected:
            required_items = expected["contains"]
            if isinstance(required_items, list):
                actual_str = str(actual).lower()
                matches = sum(1 for item in required_items if str(item).lower() in actual_str)
                return matches / len(required_items) if required_items else 0.0
        
        # Check for key-value matches
        if isinstance(expected, dict) and isinstance(actual, dict):
            matching_keys = sum(
                1 for key in expected.keys() 
                if key in actual and expected[key] == actual[key]
            )
            total_keys = len(expected)
            return matching_keys / total_keys if total_keys > 0 else 0.0
        
        return 0.0
    
    def calculate_cost(
        self, 
        input_tokens: int = 0, 
        output_tokens: int = 0
    ) -> float:
        """
        Calculate cost based on token usage.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Cost in USD
        """
        input_cost = (input_tokens / 1000) * self.COST_PER_1K_INPUT_TOKENS
        output_cost = (output_tokens / 1000) * self.COST_PER_1K_OUTPUT_TOKENS
        return input_cost + output_cost
    
    def evaluate(
        self,
        expected: Dict[str, Any],
        actual: Dict[str, Any],
        input_tokens: int = 0,
        output_tokens: int = 0,
        accuracy_threshold: float = 0.8
    ) -> EvalScore:
        """
        Complete evaluation with all metrics.
        
        Args:
            expected: Expected output
            actual: Actual output from agent
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens used
            accuracy_threshold: Minimum accuracy to pass (default: 0.8)
            
        Returns:
            EvalScore with all metrics
        """
        latency = self.stop_timer()
        accuracy = self.calculate_accuracy(expected, actual)
        cost = self.calculate_cost(input_tokens, output_tokens)
        passed = accuracy >= accuracy_threshold
        
        return EvalScore(
            accuracy=accuracy,
            latency_ms=latency,
            cost=cost,
            passed=passed
        )
