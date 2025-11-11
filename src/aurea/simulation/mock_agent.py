"""Mock agent implementation for simulation mode."""

import time
from typing import Any, Dict
from aurea.core.agent import Agent


class MockAgent(Agent):
    """Mock agent for simulation and testing."""

    def __init__(self, name: str, config: Dict[str, Any] = None):
        """Initialize mock agent.
        
        Args:
            name: Name of the agent
            config: Configuration including delay, success_rate, etc.
        """
        super().__init__(name, config)
        self.delay = self.config.get("delay", 0.1)
        self.success_rate = self.config.get("success_rate", 1.0)
        self.response_template = self.config.get("response", {})
        self.execution_count = 0

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a mock task.
        
        Args:
            task: Task dictionary
            
        Returns:
            Mock execution result
        """
        self.execution_count += 1
        
        # Simulate processing time
        time.sleep(self.delay)
        
        # Determine success based on success_rate
        import random
        success = random.random() < self.success_rate
        
        result = {
            "agent": self.name,
            "task_id": task.get("id", "unknown"),
            "status": "success" if success else "failed",
            "execution_count": self.execution_count,
            "timestamp": time.time(),
        }
        
        # Merge response template
        if self.response_template:
            result.update(self.response_template)
        
        if not success:
            result["error"] = "Simulated failure"
        
        return result

    def get_capabilities(self) -> Dict[str, Any]:
        """Get mock agent capabilities.
        
        Returns:
            Capabilities dictionary
        """
        return {
            "type": "mock",
            "name": self.name,
            "delay": self.delay,
            "success_rate": self.success_rate,
            "execution_count": self.execution_count,
        }
