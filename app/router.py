"""
Model Router with dynamic cost-quality scoring.

This module implements a router that selects models based on:
- Cost efficiency
- Quality/success rate
- Latency performance

Metrics are tracked per model and weights are updated via the /router/optimize endpoint.
"""
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict
import statistics

from pydantic import BaseModel


class ModelMetrics(BaseModel):
    """Metrics tracked for each model."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_latency: float = 0.0
    total_cost: float = 0.0
    last_updated: str = ""

    @property
    def average_latency(self) -> float:
        """Calculate average latency."""
        if self.total_requests == 0:
            return 0.0
        return self.total_latency / self.total_requests

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests

    @property
    def average_cost(self) -> float:
        """Calculate average cost per request."""
        if self.total_requests == 0:
            return 0.0
        return self.total_cost / self.total_requests


class ModelWeights(BaseModel):
    """Weights for model selection."""
    cost_weight: float = 0.33
    quality_weight: float = 0.34
    latency_weight: float = 0.33


class ModelRouter:
    """
    Router that dynamically selects models based on cost, quality, and latency.
    """

    def __init__(self, metrics_file: str = "metrics_data.json", weights_file: str = "router_weights.json"):
        self.metrics_file = Path(metrics_file)
        self.weights_file = Path(weights_file)
        self.metrics: Dict[str, ModelMetrics] = {}
        self.weights = ModelWeights()
        self.available_models = [
            "gpt-4",
            "gpt-3.5-turbo",
            "claude-3-opus",
            "claude-3-sonnet",
            "llama-2-70b"
        ]
        self._load_metrics()
        self._load_weights()

    def _load_metrics(self):
        """Load metrics from file."""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    data = json.load(f)
                    self.metrics = {
                        model: ModelMetrics(**metrics)
                        for model, metrics in data.items()
                    }
            except Exception as e:
                print(f"Error loading metrics: {e}")
                self.metrics = {}
        
        # Initialize metrics for all available models
        for model in self.available_models:
            if model not in self.metrics:
                self.metrics[model] = ModelMetrics(
                    last_updated=datetime.now().isoformat()
                )

    def _save_metrics(self):
        """Save metrics to file."""
        try:
            data = {
                model: metrics.model_dump()
                for model, metrics in self.metrics.items()
            }
            with open(self.metrics_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving metrics: {e}")

    def _load_weights(self):
        """Load weights from file."""
        if self.weights_file.exists():
            try:
                with open(self.weights_file, 'r') as f:
                    data = json.load(f)
                    self.weights = ModelWeights(**data)
            except Exception as e:
                print(f"Error loading weights: {e}")
                self.weights = ModelWeights()

    def _save_weights(self):
        """Save weights to file."""
        try:
            with open(self.weights_file, 'w') as f:
                json.dump(self.weights.model_dump(), f, indent=2)
        except Exception as e:
            print(f"Error saving weights: {e}")

    def record_request(self, model: str, latency: float, cost: float, success: bool):
        """
        Record a request's metrics.
        
        Args:
            model: Model name
            latency: Request latency in seconds
            cost: Request cost in USD
            success: Whether the request was successful
        """
        if model not in self.metrics:
            self.metrics[model] = ModelMetrics(
                last_updated=datetime.now().isoformat()
            )

        metrics = self.metrics[model]
        metrics.total_requests += 1
        metrics.total_latency += latency
        metrics.total_cost += cost
        
        if success:
            metrics.successful_requests += 1
        else:
            metrics.failed_requests += 1
        
        metrics.last_updated = datetime.now().isoformat()
        self._save_metrics()

    def calculate_model_score(self, model: str) -> float:
        """
        Calculate composite score for a model based on cost, quality, and latency.
        
        Higher score is better. Normalizes metrics across all models.
        
        Args:
            model: Model name
            
        Returns:
            Composite score (0-1)
        """
        if model not in self.metrics:
            return 0.0

        metrics = self.metrics[model]
        
        # If no requests yet, return neutral score
        if metrics.total_requests == 0:
            return 0.5

        # Collect all metrics for normalization
        all_costs = []
        all_latencies = []
        all_success_rates = []
        
        for m in self.metrics.values():
            if m.total_requests > 0:
                all_costs.append(m.average_cost)
                all_latencies.append(m.average_latency)
                all_success_rates.append(m.success_rate)

        if not all_costs:
            return 0.5

        # Normalize metrics (0-1 scale)
        # For cost and latency: lower is better, so invert
        # For success rate: higher is better
        
        max_cost = max(all_costs) if all_costs else 1.0
        min_cost = min(all_costs) if all_costs else 0.0
        cost_range = max_cost - min_cost if max_cost != min_cost else 1.0
        cost_score = 1.0 - ((metrics.average_cost - min_cost) / cost_range)

        max_latency = max(all_latencies) if all_latencies else 1.0
        min_latency = min(all_latencies) if all_latencies else 0.0
        latency_range = max_latency - min_latency if max_latency != min_latency else 1.0
        latency_score = 1.0 - ((metrics.average_latency - min_latency) / latency_range)

        quality_score = metrics.success_rate

        # Calculate weighted composite score
        composite_score = (
            cost_score * self.weights.cost_weight +
            quality_score * self.weights.quality_weight +
            latency_score * self.weights.latency_weight
        )

        return composite_score

    def select_model(self) -> str:
        """
        Select the best model based on current scores.
        
        Returns:
            Model name
        """
        scores = {}
        for model in self.available_models:
            scores[model] = self.calculate_model_score(model)

        # Select model with highest score
        best_model = max(scores.items(), key=lambda x: x[1])[0]
        return best_model

    def get_metrics_summary(self) -> Dict[str, Dict]:
        """
        Get summary of all model metrics.
        
        Returns:
            Dictionary with metrics for each model
        """
        summary = {}
        for model, metrics in self.metrics.items():
            summary[model] = {
                "total_requests": metrics.total_requests,
                "success_rate": metrics.success_rate,
                "average_latency": metrics.average_latency,
                "average_cost": metrics.average_cost,
                "score": self.calculate_model_score(model),
                "last_updated": metrics.last_updated
            }
        return summary

    def optimize_weights(self) -> Dict[str, float]:
        """
        Optimize selection weights based on recent performance.
        
        This is called weekly to adjust weights. The optimization strategy:
        - Analyzes variance in metrics across models
        - Increases weight for metrics with higher variance (more discriminating)
        - Ensures weights sum to 1.0
        
        Returns:
            New weights
        """
        # Collect metrics for all models with data
        costs = []
        latencies = []
        success_rates = []
        
        for metrics in self.metrics.values():
            if metrics.total_requests > 0:
                costs.append(metrics.average_cost)
                latencies.append(metrics.average_latency)
                success_rates.append(metrics.success_rate)

        # If not enough data, keep current weights
        if len(costs) < 2:
            return self.weights.model_dump()

        # Calculate variance for each metric (coefficient of variation)
        cost_var = statistics.stdev(costs) / statistics.mean(costs) if statistics.mean(costs) > 0 else 0
        latency_var = statistics.stdev(latencies) / statistics.mean(latencies) if statistics.mean(latencies) > 0 else 0
        success_var = statistics.stdev(success_rates) / statistics.mean(success_rates) if statistics.mean(success_rates) > 0 else 0

        # Weight by variance (higher variance = more important for differentiation)
        total_var = cost_var + latency_var + success_var
        
        if total_var > 0:
            self.weights.cost_weight = cost_var / total_var
            self.weights.quality_weight = success_var / total_var
            self.weights.latency_weight = latency_var / total_var
        else:
            # Default equal weights if no variance
            self.weights.cost_weight = 0.33
            self.weights.quality_weight = 0.34
            self.weights.latency_weight = 0.33

        self._save_weights()
        return self.weights.model_dump()

    def get_weights(self) -> Dict[str, float]:
        """Get current weights."""
        return self.weights.model_dump()
