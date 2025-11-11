"""Tests for Model Router."""
import json
import os
import tempfile
from pathlib import Path
import pytest
from app.router import ModelRouter, ModelMetrics


@pytest.fixture
def temp_files():
    """Create temporary files for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        metrics_file = os.path.join(tmpdir, "test_metrics.json")
        weights_file = os.path.join(tmpdir, "test_weights.json")
        yield metrics_file, weights_file


@pytest.fixture
def router(temp_files):
    """Create a router instance with temporary files."""
    metrics_file, weights_file = temp_files
    return ModelRouter(metrics_file=metrics_file, weights_file=weights_file)


def test_router_initialization(router):
    """Test that router initializes properly."""
    assert router is not None
    assert len(router.available_models) > 0
    assert router.weights is not None
    assert router.weights.cost_weight > 0
    assert router.weights.quality_weight > 0
    assert router.weights.latency_weight > 0


def test_record_request(router):
    """Test recording a request."""
    model = "gpt-4"
    router.record_request(model, latency=0.5, cost=0.02, success=True)
    
    assert model in router.metrics
    assert router.metrics[model].total_requests == 1
    assert router.metrics[model].successful_requests == 1
    assert router.metrics[model].total_latency == 0.5
    assert router.metrics[model].total_cost == 0.02


def test_record_multiple_requests(router):
    """Test recording multiple requests."""
    model = "gpt-3.5-turbo"
    
    # Record successful requests
    for i in range(5):
        router.record_request(model, latency=0.3, cost=0.002, success=True)
    
    # Record failed requests
    for i in range(2):
        router.record_request(model, latency=0.4, cost=0.002, success=False)
    
    metrics = router.metrics[model]
    assert metrics.total_requests == 7
    assert metrics.successful_requests == 5
    assert metrics.failed_requests == 2
    assert abs(metrics.success_rate - 5/7) < 0.01


def test_calculate_model_score(router):
    """Test model score calculation."""
    # Record data for multiple models
    router.record_request("gpt-4", latency=0.8, cost=0.03, success=True)
    router.record_request("gpt-3.5-turbo", latency=0.3, cost=0.002, success=True)
    router.record_request("claude-3-opus", latency=0.6, cost=0.025, success=True)
    
    # All models should have scores between 0 and 1
    for model in ["gpt-4", "gpt-3.5-turbo", "claude-3-opus"]:
        score = router.calculate_model_score(model)
        assert 0 <= score <= 1


def test_select_model(router):
    """Test model selection."""
    # Record varying performance for different models
    # gpt-3.5-turbo: fast, cheap, reliable
    for i in range(10):
        router.record_request("gpt-3.5-turbo", latency=0.2, cost=0.001, success=True)
    
    # gpt-4: slower, expensive, reliable
    for i in range(10):
        router.record_request("gpt-4", latency=0.8, cost=0.03, success=True)
    
    # claude-3-sonnet: medium everything
    for i in range(10):
        router.record_request("claude-3-sonnet", latency=0.5, cost=0.015, success=True)
    
    # Should select a model (likely gpt-3.5-turbo due to best combo)
    selected = router.select_model()
    assert selected in router.available_models


def test_metrics_persistence(temp_files):
    """Test that metrics persist across router instances."""
    metrics_file, weights_file = temp_files
    
    # Create router and record data
    router1 = ModelRouter(metrics_file=metrics_file, weights_file=weights_file)
    router1.record_request("gpt-4", latency=0.5, cost=0.02, success=True)
    
    # Create new router instance
    router2 = ModelRouter(metrics_file=metrics_file, weights_file=weights_file)
    
    # Data should be loaded
    assert "gpt-4" in router2.metrics
    assert router2.metrics["gpt-4"].total_requests == 1


def test_optimize_weights(router):
    """Test weight optimization."""
    # Record data with varying characteristics
    # High cost variance
    router.record_request("gpt-4", latency=0.5, cost=0.05, success=True)
    router.record_request("gpt-3.5-turbo", latency=0.5, cost=0.001, success=True)
    
    initial_weights = router.get_weights()
    optimized_weights = router.optimize_weights()
    
    # Weights should sum to ~1.0
    total = sum(optimized_weights.values())
    assert abs(total - 1.0) < 0.01


def test_get_metrics_summary(router):
    """Test getting metrics summary."""
    router.record_request("gpt-4", latency=0.5, cost=0.02, success=True)
    router.record_request("gpt-4", latency=0.6, cost=0.025, success=False)
    
    summary = router.get_metrics_summary()
    
    assert "gpt-4" in summary
    assert summary["gpt-4"]["total_requests"] == 2
    assert "success_rate" in summary["gpt-4"]
    assert "average_latency" in summary["gpt-4"]
    assert "average_cost" in summary["gpt-4"]
    assert "score" in summary["gpt-4"]


def test_average_latency(router):
    """Test average latency calculation."""
    model = "claude-3-opus"
    router.record_request(model, latency=0.5, cost=0.01, success=True)
    router.record_request(model, latency=0.7, cost=0.01, success=True)
    router.record_request(model, latency=0.6, cost=0.01, success=True)
    
    metrics = router.metrics[model]
    expected_avg = (0.5 + 0.7 + 0.6) / 3
    assert abs(metrics.average_latency - expected_avg) < 0.01


def test_average_cost(router):
    """Test average cost calculation."""
    model = "llama-2-70b"
    router.record_request(model, latency=0.3, cost=0.001, success=True)
    router.record_request(model, latency=0.3, cost=0.002, success=True)
    router.record_request(model, latency=0.3, cost=0.003, success=True)
    
    metrics = router.metrics[model]
    expected_avg = (0.001 + 0.002 + 0.003) / 3
    assert abs(metrics.average_cost - expected_avg) < 0.0001


def test_success_rate(router):
    """Test success rate calculation."""
    model = "gpt-4"
    
    # 7 successful, 3 failed
    for i in range(7):
        router.record_request(model, latency=0.5, cost=0.02, success=True)
    for i in range(3):
        router.record_request(model, latency=0.5, cost=0.02, success=False)
    
    metrics = router.metrics[model]
    assert abs(metrics.success_rate - 0.7) < 0.01
