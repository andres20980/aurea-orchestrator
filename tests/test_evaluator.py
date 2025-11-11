"""Tests for the evaluation system"""

import tempfile
from pathlib import Path

from aurea.models import ModelType, TaskType
from aurea.evaluator import EvaluationRunner
from aurea.tracker import EvaluationTracker


def mock_model_client(prompt: str) -> str:
    """Mock model client for testing"""
    return f"Response to: {prompt}"


def test_evaluation_runner():
    """Test basic evaluation runner functionality"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tracker = EvaluationTracker(storage_path=tmpdir)
        runner = EvaluationRunner(tracker=tracker)
        
        # Register clients
        runner.register_model_client(ModelType.CLAUDE, mock_model_client)
        runner.register_model_client(ModelType.DEEPSEEK, mock_model_client)
        runner.register_model_client(ModelType.GPT, mock_model_client)
        
        # Run evaluation
        comparison = runner.run_evaluation(
            task_id="test_1",
            task_type=TaskType.CODE_GENERATION,
            prompt="Test prompt"
        )
        
        assert comparison.task_id == "test_1"
        assert comparison.task_type == TaskType.CODE_GENERATION
        assert len(comparison.results) == 3
        assert comparison.winner in ModelType
        
        print("✓ Evaluation runner test passed")


def test_win_rate_tracking():
    """Test win rate tracking"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tracker = EvaluationTracker(storage_path=tmpdir)
        runner = EvaluationRunner(tracker=tracker)
        
        # Register clients with different output lengths
        runner.register_model_client(
            ModelType.CLAUDE, 
            lambda p: "Long detailed response " * 20
        )
        runner.register_model_client(
            ModelType.DEEPSEEK, 
            lambda p: "Short response"
        )
        runner.register_model_client(
            ModelType.GPT, 
            lambda p: "Medium response " * 5
        )
        
        # Run multiple evaluations
        for i in range(5):
            runner.run_evaluation(
                task_id=f"test_{i}",
                task_type=TaskType.CODE_GENERATION,
                prompt=f"Test prompt {i}"
            )
        
        # Check win rates
        win_rates = runner.get_win_rates(TaskType.CODE_GENERATION)
        assert win_rates['total_evaluations'] == 5
        assert 'win_rates' in win_rates
        
        # Claude should have highest win rate due to longer outputs
        assert win_rates['win_rates']['claude'] > 0
        
        print("✓ Win rate tracking test passed")


def test_tracker_persistence():
    """Test that tracker persists data"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create and use tracker
        tracker1 = EvaluationTracker(storage_path=tmpdir)
        runner1 = EvaluationRunner(tracker=tracker1)
        runner1.register_model_client(ModelType.CLAUDE, mock_model_client)
        runner1.register_model_client(ModelType.DEEPSEEK, mock_model_client)
        runner1.register_model_client(ModelType.GPT, mock_model_client)
        
        runner1.run_evaluation(
            task_id="persist_test",
            task_type=TaskType.SUMMARIZATION,
            prompt="Persistence test"
        )
        
        # Create new tracker with same path
        tracker2 = EvaluationTracker(storage_path=tmpdir)
        
        # Should load previous data
        assert len(tracker2.comparisons) == 1
        assert tracker2.comparisons[0].task_id == "persist_test"
        
        print("✓ Tracker persistence test passed")


def run_all_tests():
    """Run all tests"""
    print("Running tests...\n")
    test_evaluation_runner()
    test_win_rate_tracking()
    test_tracker_persistence()
    print("\nAll tests passed!")


if __name__ == "__main__":
    run_all_tests()
