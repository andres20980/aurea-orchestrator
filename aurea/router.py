"""Model router with automatic weight updates"""

import json
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Optional

from .models import ModelType, RouterWeights, TaskType
from .tracker import EvaluationTracker


class ModelRouter:
    """Routes tasks to models based on performance weights"""
    
    def __init__(
        self,
        tracker: Optional[EvaluationTracker] = None,
        weights_path: str = "router_weights.json",
        auto_update: bool = True
    ):
        self.tracker = tracker or EvaluationTracker()
        self.weights_path = Path(weights_path)
        self.auto_update = auto_update
        self.weights = self._load_weights()
        self.model_clients: Dict[ModelType, Callable] = {}
    
    def _load_weights(self) -> RouterWeights:
        """Load router weights from disk"""
        if self.weights_path.exists():
            with open(self.weights_path, 'r') as f:
                data = json.load(f)
                return RouterWeights(**data)
        
        # Initialize with default weights
        return RouterWeights(
            weights={},
            last_updated=datetime.utcnow().isoformat()
        )
    
    def _save_weights(self):
        """Save router weights to disk"""
        with open(self.weights_path, 'w') as f:
            json.dump(self.weights.model_dump(), f, indent=2)
    
    def update_weights_from_performance(self, min_evaluations: int = 5):
        """Update router weights based on model performance"""
        updated = False
        
        for task_type in TaskType:
            stats = self.tracker.stats.get(task_type)
            
            # Only update if we have enough evaluations
            if not stats or stats.total_evaluations < min_evaluations:
                continue
            
            # Use win rates as weights
            if stats.win_rates:
                if task_type not in self.weights.weights:
                    self.weights.weights[task_type] = {}
                
                # Update weights with win rates
                for model, win_rate in stats.win_rates.items():
                    self.weights.weights[task_type][model] = win_rate
                
                updated = True
        
        if updated:
            self.weights.last_updated = datetime.utcnow().isoformat()
            self._save_weights()
    
    def register_model_client(self, model: ModelType, client: Callable[[str], str]):
        """Register a client function for a model"""
        self.model_clients[model] = client
    
    def route(self, task_type: TaskType, prompt: str) -> str:
        """Route a task to the best model and return result"""
        if self.auto_update:
            self.update_weights_from_performance()
        
        # Get best model for this task type
        best_model = self.weights.get_best_model(task_type)
        
        # Get the client for this model
        if best_model not in self.model_clients:
            raise ValueError(f"No client registered for model: {best_model.value}")
        
        client = self.model_clients[best_model]
        return client(prompt)
    
    def get_model_for_task(self, task_type: TaskType) -> ModelType:
        """Get the recommended model for a task type without executing"""
        if self.auto_update:
            self.update_weights_from_performance()
        
        return self.weights.get_best_model(task_type)
    
    def get_current_weights(self) -> Dict:
        """Get current router weights"""
        return {
            "weights": {
                task_type.value: {
                    model.value: weight
                    for model, weight in weights.items()
                }
                for task_type, weights in self.weights.weights.items()
            },
            "last_updated": self.weights.last_updated
        }
