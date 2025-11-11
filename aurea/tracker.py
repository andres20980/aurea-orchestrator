"""Evaluation tracker for model performance"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .models import (
    EvaluationResult,
    ModelComparison,
    ModelType,
    TaskType,
    TaskTypeStats,
)


class EvaluationTracker:
    """Tracks evaluation results and computes win rates"""
    
    def __init__(self, storage_path: str = "evaluation_results"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.comparisons: List[ModelComparison] = []
        self.stats: Dict[TaskType, TaskTypeStats] = {}
        self._load_data()
    
    def _load_data(self):
        """Load existing evaluation data"""
        comparisons_file = self.storage_path / "comparisons.jsonl"
        if comparisons_file.exists():
            with open(comparisons_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        self.comparisons.append(ModelComparison(**data))
        
        self._compute_stats()
    
    def _save_comparison(self, comparison: ModelComparison):
        """Save a comparison to disk"""
        comparisons_file = self.storage_path / "comparisons.jsonl"
        with open(comparisons_file, 'a') as f:
            f.write(comparison.model_dump_json() + '\n')
    
    def add_comparison(self, comparison: ModelComparison):
        """Add a new comparison result"""
        self.comparisons.append(comparison)
        self._save_comparison(comparison)
        self._update_stats(comparison)
    
    def _compute_stats(self):
        """Compute statistics from all comparisons"""
        self.stats = {}
        for task_type in TaskType:
            self.stats[task_type] = TaskTypeStats(
                task_type=task_type,
                total_evaluations=0,
                win_counts={},
                win_rates={}
            )
        
        for comparison in self.comparisons:
            task_type = comparison.task_type
            self.stats[task_type].total_evaluations += 1
            winner = comparison.winner
            if winner not in self.stats[task_type].win_counts:
                self.stats[task_type].win_counts[winner] = 0
            self.stats[task_type].win_counts[winner] += 1
        
        for task_type in TaskType:
            self.stats[task_type].update_win_rates()
    
    def _update_stats(self, comparison: ModelComparison):
        """Update statistics with a new comparison"""
        task_type = comparison.task_type
        if task_type not in self.stats:
            self.stats[task_type] = TaskTypeStats(
                task_type=task_type,
                total_evaluations=0,
                win_counts={},
                win_rates={}
            )
        
        self.stats[task_type].total_evaluations += 1
        winner = comparison.winner
        if winner not in self.stats[task_type].win_counts:
            self.stats[task_type].win_counts[winner] = 0
        self.stats[task_type].win_counts[winner] += 1
        self.stats[task_type].update_win_rates()
    
    def get_win_rates(self, task_type: Optional[TaskType] = None) -> Dict:
        """Get win rates for all or specific task type"""
        if task_type:
            return {
                "task_type": task_type.value,
                "total_evaluations": self.stats[task_type].total_evaluations,
                "win_rates": {
                    model.value: rate 
                    for model, rate in self.stats[task_type].win_rates.items()
                }
            }
        
        return {
            task_type.value: {
                "total_evaluations": stats.total_evaluations,
                "win_rates": {
                    model.value: rate 
                    for model, rate in stats.win_rates.items()
                }
            }
            for task_type, stats in self.stats.items()
        }
    
    def get_best_model(self, task_type: TaskType) -> Optional[ModelType]:
        """Get the best performing model for a task type"""
        if task_type not in self.stats or self.stats[task_type].total_evaluations == 0:
            return None
        
        win_rates = self.stats[task_type].win_rates
        if not win_rates:
            return None
        
        return max(win_rates.items(), key=lambda x: x[1])[0]
