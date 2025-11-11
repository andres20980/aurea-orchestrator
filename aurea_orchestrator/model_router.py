"""Model Router for selecting between Gemini and OpenAI based on task complexity."""

from enum import Enum
from typing import Any

from langchain_core.language_models import BaseLanguageModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from aurea_orchestrator.config import settings


class ModelType(str, Enum):
    """Model types available."""

    GEMINI = "gemini"
    OPENAI = "openai"


class TaskComplexity(str, Enum):
    """Task complexity levels."""

    SIMPLE = "simple"
    COMPLEX = "complex"


class ModelRouter:
    """Routes tasks to appropriate models based on complexity."""

    def __init__(
        self,
        complexity_threshold: float = None,
        gemini_model: str = None,
        openai_model: str = None,
    ):
        """Initialize the model router.

        Args:
            complexity_threshold: Threshold for complexity (0.0-1.0)
            gemini_model: Gemini model name
            openai_model: OpenAI model name
        """
        self.complexity_threshold = complexity_threshold or settings.complexity_threshold
        self.gemini_model = gemini_model or settings.gemini_model
        self.openai_model = openai_model or settings.openai_model

        self._gemini_instance = None
        self._openai_instance = None

    def _get_gemini(self) -> BaseLanguageModel:
        """Get or create Gemini instance."""
        if self._gemini_instance is None:
            self._gemini_instance = ChatGoogleGenerativeAI(
                model=self.gemini_model,
                google_api_key=settings.google_api_key,
                temperature=0.7,
                convert_system_message_to_human=True,  # Gemini compatibility
            )
        return self._gemini_instance

    def _get_openai(self) -> BaseLanguageModel:
        """Get or create OpenAI instance."""
        if self._openai_instance is None:
            self._openai_instance = ChatOpenAI(
                model=self.openai_model,
                openai_api_key=settings.openai_api_key,
                temperature=0.7,
            )
        return self._openai_instance

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

        # Use default provider preference if configured
        default_provider = getattr(settings, 'default_model_provider', 'gemini')
        
        if complexity >= self.complexity_threshold:
            # Complex task: use configured primary model (default: Gemini Pro or OpenAI)
            return ModelType.GEMINI if default_provider == 'gemini' else ModelType.OPENAI
        
        # Simple task: use Gemini Flash (fastest/cheapest) or fallback
        return ModelType.GEMINI

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

        if model_type == ModelType.GEMINI:
            return self._get_gemini()
        return self._get_openai()


# Global router instance
model_router = ModelRouter()
