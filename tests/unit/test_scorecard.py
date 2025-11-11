"""Unit tests for scorecard functionality"""

import pytest
from src.eval.scorecard import Scorecard
from src.models.eval_models import EvalScore


def test_scorecard_timer():
    """Test latency timer functionality"""
    scorecard = Scorecard()
    scorecard.start_timer()
    
    # Simulate some work
    import time
    time.sleep(0.01)  # 10ms
    
    latency = scorecard.stop_timer()
    assert latency >= 10.0  # Should be at least 10ms
    assert latency < 100.0  # But not too much more


def test_calculate_accuracy_exact_match():
    """Test accuracy calculation for exact matches"""
    scorecard = Scorecard()
    
    expected = {"result": "success", "value": 42}
    actual = {"result": "success", "value": 42}
    
    accuracy = scorecard.calculate_accuracy(expected, actual)
    assert accuracy == 1.0


def test_calculate_accuracy_contains():
    """Test accuracy calculation for contains mode"""
    scorecard = Scorecard()
    
    expected = {"contains": ["def", "add", "return"]}
    actual = {"code": "def add(a, b):\n    return a + b"}
    
    accuracy = scorecard.calculate_accuracy(expected, actual)
    assert accuracy == 1.0  # All 3 items found


def test_calculate_accuracy_partial_contains():
    """Test accuracy calculation for partial contains matches"""
    scorecard = Scorecard()
    
    expected = {"contains": ["def", "add", "multiply"]}
    actual = {"code": "def add(a, b):\n    return a + b"}
    
    accuracy = scorecard.calculate_accuracy(expected, actual)
    assert accuracy == pytest.approx(0.666, rel=0.01)  # 2/3 items found


def test_calculate_accuracy_key_value():
    """Test accuracy calculation for key-value matches"""
    scorecard = Scorecard()
    
    expected = {"status": "ok", "count": 5}
    actual = {"status": "ok", "count": 5, "extra": "data"}
    
    accuracy = scorecard.calculate_accuracy(expected, actual)
    assert accuracy == 1.0  # Both keys match


def test_calculate_cost():
    """Test cost calculation"""
    scorecard = Scorecard()
    
    cost = scorecard.calculate_cost(input_tokens=1000, output_tokens=500)
    expected_cost = (1000 / 1000 * 0.0001) + (500 / 1000 * 0.0002)
    assert cost == pytest.approx(expected_cost)


def test_evaluate_complete():
    """Test complete evaluation with all metrics"""
    scorecard = Scorecard()
    scorecard.start_timer()
    
    import time
    time.sleep(0.01)
    
    expected = {"contains": ["def", "add"]}
    actual = {"code": "def add(a, b): return a + b"}
    
    score = scorecard.evaluate(
        expected=expected,
        actual=actual,
        input_tokens=100,
        output_tokens=50,
        accuracy_threshold=0.8
    )
    
    assert isinstance(score, EvalScore)
    assert score.accuracy > 0.0
    assert score.latency_ms > 0.0
    assert score.cost > 0.0
    assert score.passed is True


def test_evaluate_below_threshold():
    """Test evaluation that fails threshold"""
    scorecard = Scorecard()
    scorecard.start_timer()
    
    expected = {"contains": ["multiply", "divide"]}
    actual = {"code": "def add(a, b): return a + b"}
    
    score = scorecard.evaluate(
        expected=expected,
        actual=actual,
        input_tokens=100,
        output_tokens=50,
        accuracy_threshold=0.8
    )
    
    assert score.passed is False
    assert score.accuracy < 0.8
