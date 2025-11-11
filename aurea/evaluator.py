"""Evaluation job runner for comparing model outputs"""

from datetime import datetime
from typing import Callable, Dict, List, Optional

from .models import (
    EvaluationResult,
    ModelComparison,
    ModelType,
    TaskType,
)
from .tracker import EvaluationTracker


class EvaluationJob:
    """Represents a single evaluation job comparing models"""
    
    def __init__(
        self,
        task_id: str,
        task_type: TaskType,
        prompt: str,
        models: List[ModelType] = None,
        scorer: Optional[Callable[[str, str], float]] = None
    ):
        self.task_id = task_id
        self.task_type = task_type
        self.prompt = prompt
        self.models = models or list(ModelType)
        self.scorer = scorer or self._default_scorer
        self.model_clients: Dict[ModelType, Callable] = {}
    
    def _default_scorer(self, prompt: str, output: str) -> float:
        """Default scoring function - can be overridden"""
        # Simple heuristic: longer outputs score higher (up to a point)
        # In practice, this would use more sophisticated evaluation
        if not output:
            return 0.0
        
        length_score = min(len(output) / 1000, 1.0)
        return length_score
    
    def register_model_client(self, model: ModelType, client: Callable[[str], str]):
        """Register a client function for a model"""
        self.model_clients[model] = client
    
    def run(self) -> ModelComparison:
        """Run the evaluation job and return comparison"""
        timestamp = datetime.utcnow().isoformat()
        results = {}
        
        for model in self.models:
            if model not in self.model_clients:
                # Mock output if client not registered
                output = f"Mock output from {model.value} for: {self.prompt[:50]}..."
            else:
                output = self.model_clients[model](self.prompt)
            
            score = self.scorer(self.prompt, output)
            
            results[model] = EvaluationResult(
                task_id=self.task_id,
                task_type=self.task_type,
                model=model,
                prompt=self.prompt,
                output=output,
                score=score,
                timestamp=timestamp
            )
        
        # Determine winner (highest score)
        winner = max(results.items(), key=lambda x: x[1].score)[0]
        
        return ModelComparison(
            task_id=self.task_id,
            task_type=self.task_type,
            prompt=self.prompt,
            results=results,
            winner=winner,
            timestamp=timestamp
        )


class EvaluationRunner:
    """Runs evaluation jobs and tracks results"""
    
    def __init__(self, tracker: Optional[EvaluationTracker] = None):
        self.tracker = tracker or EvaluationTracker()
        self.model_clients: Dict[ModelType, Callable] = {}
    
    def register_model_client(self, model: ModelType, client: Callable[[str], str]):
        """Register a client function for a model"""
        self.model_clients[model] = client
    
    def run_evaluation(
        self,
        task_id: str,
        task_type: TaskType,
        prompt: str,
        models: List[ModelType] = None,
        scorer: Optional[Callable[[str, str], float]] = None
    ) -> ModelComparison:
        """Run a single evaluation job"""
        job = EvaluationJob(task_id, task_type, prompt, models, scorer)
        
        # Register clients with the job
        for model, client in self.model_clients.items():
            job.register_model_client(model, client)
        
        comparison = job.run()
        self.tracker.add_comparison(comparison)
        
        return comparison
    
    def run_batch_evaluations(
        self,
        tasks: List[Dict],
        models: List[ModelType] = None,
        scorer: Optional[Callable[[str, str], float]] = None
    ) -> List[ModelComparison]:
        """Run multiple evaluation jobs"""
        results = []
        for task in tasks:
            comparison = self.run_evaluation(
                task_id=task['task_id'],
                task_type=TaskType(task['task_type']),
                prompt=task['prompt'],
                models=models,
                scorer=scorer
            )
            results.append(comparison)
        
        return results
    
    def get_win_rates(self, task_type: Optional[TaskType] = None) -> Dict:
        """Get win rates from tracker"""
        return self.tracker.get_win_rates(task_type)
