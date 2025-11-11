"""Base agent interface for Aurea orchestrator."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class Agent(ABC):
    """Abstract base class for agents."""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """Initialize the agent.
        
        Args:
            name: Name of the agent
            config: Optional configuration dictionary
        """
        self.name = name
        self.config = config or {}

    @abstractmethod
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task.
        
        Args:
            task: Task dictionary containing task details
            
        Returns:
            Result dictionary containing execution results
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities.
        
        Returns:
            Dictionary describing agent capabilities
        """
        pass
