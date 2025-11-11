"""Tests for cost tracker."""

import pytest
from aurea.cost_tracker import CostTracker, CostExceededError


class TestCostTracker:
    """Test cost tracking functionality."""
    
    def test_initialization(self):
        """Test cost tracker initialization."""
        tracker = CostTracker("job-1", max_cost=5.0)
        assert tracker.job_id == "job-1"
        assert tracker.max_cost == 5.0
        assert tracker.total_cost == 0.0
    
    def test_estimate_cost(self):
        """Test cost estimation."""
        tracker = CostTracker("job-1")
        
        # Test with known model
        cost = tracker.estimate_cost("gpt-3.5-turbo", 1000, 500)
        expected = (1000 / 1000.0) * 0.0005 + (500 / 1000.0) * 0.0015
        assert abs(cost - expected) < 0.0001
    
    def test_estimate_cost_unknown_model(self):
        """Test cost estimation for unknown model uses default."""
        tracker = CostTracker("job-1")
        
        # Unknown model should use default pricing
        cost = tracker.estimate_cost("unknown-model", 1000, 500)
        assert cost > 0  # Should have some cost
    
    def test_track_usage(self):
        """Test usage tracking."""
        tracker = CostTracker("job-1", max_cost=10.0)
        
        cost = tracker.track_usage("gpt-3.5-turbo", 1000, 500)
        assert tracker.total_cost == cost
        assert "gpt-3.5-turbo" in tracker.usage_by_model
        assert tracker.usage_by_model["gpt-3.5-turbo"]["input_tokens"] == 1000
        assert tracker.usage_by_model["gpt-3.5-turbo"]["output_tokens"] == 500
    
    def test_cost_limit_exceeded(self):
        """Test that cost limit is enforced."""
        tracker = CostTracker("job-1", max_cost=0.001)
        
        # First small request should succeed
        tracker.track_usage("gpt-3.5-turbo", 100, 50)
        
        # Large request should fail
        with pytest.raises(CostExceededError):
            tracker.track_usage("gpt-4", 100000, 50000)
    
    def test_get_summary(self):
        """Test getting cost summary."""
        tracker = CostTracker("job-1", max_cost=10.0)
        tracker.track_usage("gpt-3.5-turbo", 1000, 500)
        
        summary = tracker.get_summary()
        assert summary["job_id"] == "job-1"
        assert summary["max_cost"] == 10.0
        assert summary["total_cost"] > 0
        assert "gpt-3.5-turbo" in summary["usage_by_model"]
    
    def test_multiple_models(self):
        """Test tracking multiple models."""
        tracker = CostTracker("job-1", max_cost=10.0)
        
        tracker.track_usage("gpt-3.5-turbo", 1000, 500)
        tracker.track_usage("gpt-4", 500, 250)
        
        assert len(tracker.usage_by_model) == 2
        assert "gpt-3.5-turbo" in tracker.usage_by_model
        assert "gpt-4" in tracker.usage_by_model
