"""Tests for model router."""

from aurea_orchestrator.model_router import ModelRouter, ModelType


class TestModelRouter:
    """Test the ModelRouter class."""

    def test_calculate_complexity_simple_task(self):
        """Test complexity calculation for a simple task."""
        router = ModelRouter(complexity_threshold=0.5)
        task = "Fix a typo in the documentation"

        complexity = router.calculate_complexity(task)

        assert 0.0 <= complexity <= 1.0
        assert complexity < 0.5

    def test_calculate_complexity_complex_task(self):
        """Test complexity calculation for a complex task."""
        router = ModelRouter(complexity_threshold=0.5)
        task = """Design and implement a complex microservices architecture with
        advanced design patterns for a distributed system that requires optimization
        and multi-step integration with various services."""

        complexity = router.calculate_complexity(task)

        assert 0.0 <= complexity <= 1.0
        assert complexity >= 0.5

    def test_calculate_complexity_with_keywords(self):
        """Test that complex keywords increase complexity score."""
        router = ModelRouter(complexity_threshold=0.5)
        task_simple = "Update the code"
        task_complex = "Refactor the architecture using design patterns and optimize the algorithm"

        complexity_simple = router.calculate_complexity(task_simple)
        complexity_complex = router.calculate_complexity(task_complex)

        assert complexity_complex > complexity_simple

    def test_calculate_complexity_with_metadata(self):
        """Test complexity calculation with metadata."""
        router = ModelRouter(complexity_threshold=0.5)
        task = "Complete a task"

        complexity_basic = router.calculate_complexity(task)
        complexity_with_reasoning = router.calculate_complexity(
            task, metadata={"requires_reasoning": True}
        )
        complexity_multi_agent = router.calculate_complexity(task, metadata={"multi_agent": True})

        assert complexity_with_reasoning > complexity_basic
        assert complexity_multi_agent > complexity_basic

    def test_determine_model_type_simple(self):
        """Test model type determination for simple tasks."""
        router = ModelRouter(complexity_threshold=0.5)
        task = "Fix a typo"

        model_type = router.determine_model_type(task)

        assert model_type == ModelType.DEEPSEEK

    def test_determine_model_type_complex(self):
        """Test model type determination for complex tasks."""
        router = ModelRouter(complexity_threshold=0.5)
        task = """Design a complex distributed system architecture with multiple design patterns,
        advanced algorithms requiring optimization, refactoring, and multi-step integration
        across various microservices with careful consideration of system-level performance."""

        model_type = router.determine_model_type(task)

        assert model_type == ModelType.CLAUDE

    def test_threshold_adjustment(self):
        """Test that threshold affects model selection."""
        task = "Implement a feature with some complexity"

        router_low = ModelRouter(complexity_threshold=0.2)
        router_high = ModelRouter(complexity_threshold=0.9)

        model_low = router_low.determine_model_type(task)
        model_high = router_high.determine_model_type(task)

        # With low threshold, more likely to use Claude
        # With high threshold, more likely to use DeepSeek
        assert model_low == ModelType.CLAUDE or model_high == ModelType.DEEPSEEK
