"""Data models for the orchestrator"""

from enum import Enum
from typing import Dict, Optional
from pydantic import BaseModel, Field


class ModelType(str, Enum):
    """Supported model types"""
    CLAUDE = "claude"
    DEEPSEEK = "deepseek"
    GPT = "gpt"


class TaskType(str, Enum):
    """Supported task types"""
    CODE_GENERATION = "code_generation"
    SUMMARIZATION = "summarization"
    QUESTION_ANSWERING = "question_answering"
    TRANSLATION = "translation"
    REASONING = "reasoning"


class EvaluationResult(BaseModel):
    """Result of a single evaluation"""
    task_id: str
    task_type: TaskType
    model: ModelType
    prompt: str
    output: str
    score: float = Field(ge=0.0, le=1.0)
    timestamp: str
    metadata: Optional[Dict] = None


class ModelComparison(BaseModel):
    """Comparison between models for a single task"""
    task_id: str
    task_type: TaskType
    prompt: str
    results: Dict[ModelType, EvaluationResult]
    winner: ModelType
    timestamp: str


class TaskTypeStats(BaseModel):
    """Statistics for a specific task type"""
    task_type: TaskType
    total_evaluations: int
    win_counts: Dict[ModelType, int] = Field(default_factory=dict)
    win_rates: Dict[ModelType, float] = Field(default_factory=dict)
    
    def update_win_rates(self):
        """Calculate win rates from win counts"""
        if self.total_evaluations > 0:
            for model in ModelType:
                count = self.win_counts.get(model, 0)
                self.win_rates[model] = count / self.total_evaluations


class RouterWeights(BaseModel):
    """Router weights for model selection"""
    weights: Dict[TaskType, Dict[ModelType, float]] = Field(default_factory=dict)
    last_updated: str
    
    def get_best_model(self, task_type: TaskType) -> ModelType:
        """Get the best model for a given task type"""
        if task_type not in self.weights or not self.weights[task_type]:
            # Default to Claude if no weights exist
            return ModelType.CLAUDE
        
        task_weights = self.weights[task_type]
        return max(task_weights.items(), key=lambda x: x[1])[0]
