"""Model Router for selecting between Claude and DeepSeek based on task complexity."""

from enum import Enum
from typing import Any

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseLanguageModel
from langchain_openai import ChatOpenAI

from aurea_orchestrator.config import settings


class ModelType(str, Enum):
    """Model types available."""

    CLAUDE = "claude"
    DEEPSEEK = "deepseek"


class TaskComplexity(str, Enum):
    """Task complexity levels."""

    SIMPLE = "simple"
    COMPLEX = "complex"


class ModelRouter:
    """Routes tasks to appropriate models based on complexity."""

    def __init__(
        self,
        complexity_threshold: float = None,
        claude_model: str = None,
        deepseek_model: str = None,
    ):
        """Initialize the model router.

        Args:
            complexity_threshold: Threshold for complexity (0.0-1.0)
            claude_model: Claude model name
            deepseek_model: DeepSeek/OpenAI model name
        """
        self.complexity_threshold = complexity_threshold or settings.complexity_threshold
        self.claude_model = claude_model or settings.claude_model
        self.deepseek_model = deepseek_model or settings.deepseek_model

        self._claude_instance = None
        self._deepseek_instance = None

    def _get_claude(self) -> BaseLanguageModel:
        """Get or create Claude instance."""
        if self._claude_instance is None:
            self._claude_instance = ChatAnthropic(
                model=self.claude_model,
                anthropic_api_key=settings.anthropic_api_key,
                temperature=0.7,
            )
        return self._claude_instance

    def _get_deepseek(self) -> BaseLanguageModel:
        """Get or create DeepSeek/OpenAI instance."""
        if self._deepseek_instance is None:
            self._deepseek_instance = ChatOpenAI(
                model=self.deepseek_model,
                openai_api_key=settings.openai_api_key,
                temperature=0.7,
            )
        return self._deepseek_instance

    def calculate_complexity(self, task_description: str, metadata: dict[str, Any] = None) -> float:
        """Calculate task complexity score.

        Args:
            task_description: Description of the task
            metadata: Additional metadata about the task

        Returns:
            Complexity score between 0.0 and 1.0
        """
        metadata = metadata or {}
        score = 0.0

        # Length-based complexity
        if len(task_description) > 500:
            score += 0.3
        elif len(task_description) > 200:
            score += 0.15

        # Keyword-based complexity
        complex_keywords = [
            "architecture",
            "design pattern",
            "refactor",
            "optimize",
            "algorithm",
            "multi-step",
            "complex",
            "integration",
            "system",
        ]
        keyword_count = sum(1 for kw in complex_keywords if kw.lower() in task_description.lower())
        score += min(keyword_count * 0.1, 0.4)

        # Metadata-based complexity
        if metadata.get("requires_reasoning"):
            score += 0.2
        if metadata.get("multi_agent"):
            score += 0.1

        return min(score, 1.0)

    def determine_model_type(
        self, task_description: str, metadata: dict[str, Any] = None
    ) -> ModelType:
        """Determine which model to use based on task complexity.

        Args:
            task_description: Description of the task
            metadata: Additional metadata about the task

        Returns:
            ModelType enum indicating which model to use
        """
        complexity = self.calculate_complexity(task_description, metadata)

        if complexity >= self.complexity_threshold:
            return ModelType.CLAUDE
        return ModelType.DEEPSEEK

    def get_model(
        self, task_description: str, metadata: dict[str, Any] = None
    ) -> BaseLanguageModel:
        """Get the appropriate model for the task.

        Args:
            task_description: Description of the task
            metadata: Additional metadata about the task

        Returns:
            Language model instance
        """
        model_type = self.determine_model_type(task_description, metadata)

        if model_type == ModelType.CLAUDE:
            return self._get_claude()
        return self._get_deepseek()


# Global router instance
model_router = ModelRouter()
