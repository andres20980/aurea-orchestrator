"""Tests for the router system"""

import tempfile
from pathlib import Path

from aurea.models import ModelType, TaskType
from aurea.evaluator import EvaluationRunner
from aurea.tracker import EvaluationTracker
from aurea.router import ModelRouter


def test_router_weight_updates():
    """Test that router updates weights from performance"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tracker = EvaluationTracker(storage_path=tmpdir)
        runner = EvaluationRunner(tracker=tracker)
        
        # Register clients with different output lengths
        runner.register_model_client(
            ModelType.CLAUDE, 
            lambda p: "Claude detailed response " * 20
        )
        runner.register_model_client(
            ModelType.DEEPSEEK, 
            lambda p: "DeepSeek short"
        )
        runner.register_model_client(
            ModelType.GPT, 
            lambda p: "GPT medium " * 10
        )
        
        # Run evaluations for code generation
        for i in range(5):
            runner.run_evaluation(
                task_id=f"code_{i}",
                task_type=TaskType.CODE_GENERATION,
                prompt=f"Code prompt {i}"
            )
        
        # Create router
        weights_file = Path(tmpdir) / "weights.json"
        router = ModelRouter(
            tracker=tracker,
            weights_path=str(weights_file),
            auto_update=False
        )
        
        # Update weights
        router.update_weights_from_performance(min_evaluations=3)
        
        # Check weights were created
        weights = router.get_current_weights()
        assert 'code_generation' in weights['weights']
        
        # Claude should have highest weight
        code_weights = weights['weights']['code_generation']
        assert code_weights['claude'] > code_weights['deepseek']
        assert code_weights['claude'] > code_weights['gpt']
        
        print("✓ Router weight update test passed")


def test_router_model_selection():
    """Test that router selects best model"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tracker = EvaluationTracker(storage_path=tmpdir)
        runner = EvaluationRunner(tracker=tracker)
        
        # DeepSeek wins for this scenario
        runner.register_model_client(
            ModelType.CLAUDE, 
            lambda p: "Short"
        )
        runner.register_model_client(
            ModelType.DEEPSEEK, 
            lambda p: "DeepSeek very long detailed response " * 30
        )
        runner.register_model_client(
            ModelType.GPT, 
            lambda p: "Medium " * 5
        )
        
        # Run evaluations
        for i in range(5):
            runner.run_evaluation(
                task_id=f"qa_{i}",
                task_type=TaskType.QUESTION_ANSWERING,
                prompt=f"QA prompt {i}"
            )
        
        # Create router
        weights_file = Path(tmpdir) / "weights.json"
        router = ModelRouter(
            tracker=tracker,
            weights_path=str(weights_file),
            auto_update=True
        )
        
        # Get best model
        best_model = router.get_model_for_task(TaskType.QUESTION_ANSWERING)
        assert best_model == ModelType.DEEPSEEK
        
        print("✓ Router model selection test passed")


def test_router_persistence():
    """Test that router persists weights"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tracker = EvaluationTracker(storage_path=tmpdir)
        weights_file = Path(tmpdir) / "weights.json"
        
        # Create router and set weights
        router1 = ModelRouter(
            tracker=tracker,
            weights_path=str(weights_file),
            auto_update=False
        )
        router1.weights.weights[TaskType.CODE_GENERATION] = {
            ModelType.CLAUDE: 0.8,
            ModelType.DEEPSEEK: 0.1,
            ModelType.GPT: 0.1
        }
        router1._save_weights()
        
        # Create new router
        router2 = ModelRouter(
            tracker=tracker,
            weights_path=str(weights_file),
            auto_update=False
        )
        
        # Should load previous weights
        weights = router2.get_current_weights()
        assert 'code_generation' in weights['weights']
        assert weights['weights']['code_generation']['claude'] == 0.8
        
        print("✓ Router persistence test passed")


def run_all_tests():
    """Run all tests"""
    print("Running router tests...\n")
    test_router_weight_updates()
    test_router_model_selection()
    test_router_persistence()
    print("\nAll router tests passed!")


if __name__ == "__main__":
    run_all_tests()
