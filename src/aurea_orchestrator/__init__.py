"""Aurea Orchestrator - Experiment Manager for AI Agents"""

__version__ = "0.1.0"

from .experiment.manager import ExperimentManager
from .experiment.runner import ExperimentRunner
from .models.experiment import Experiment, ExperimentRun, AgentConfiguration

__all__ = [
    "ExperimentManager",
    "ExperimentRunner",
    "Experiment",
    "ExperimentRun",
    "AgentConfiguration",
]
