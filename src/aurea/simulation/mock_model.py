"""Mock model implementation for simulation mode."""

import time
from typing import Any, Dict
from aurea.core.model import Model


class MockModel(Model):
    """Mock model for simulation and testing."""

    def __init__(self, name: str, config: Dict[str, Any] = None):
        """Initialize mock model.
        
        Args:
            name: Name of the model
            config: Configuration including delay, accuracy, etc.
        """
        super().__init__(name, config)
        self.delay = self.config.get("delay", 0.1)
        self.accuracy = self.config.get("accuracy", 0.95)
        self.prediction_template = self.config.get("prediction", {})
        self.prediction_count = 0

    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a mock prediction.
        
        Args:
            input_data: Input data
            
        Returns:
            Mock prediction result
        """
        self.prediction_count += 1
        
        # Simulate inference time
        time.sleep(self.delay)
        
        # Determine confidence based on accuracy
        import random
        confidence = self.accuracy + random.uniform(-0.05, 0.05)
        confidence = max(0.0, min(1.0, confidence))
        
        result = {
            "model": self.name,
            "confidence": confidence,
            "prediction_count": self.prediction_count,
            "timestamp": time.time(),
        }
        
        # Merge prediction template
        if self.prediction_template:
            result.update(self.prediction_template)
        else:
            # Default mock prediction
            result["prediction"] = "mock_output"
        
        return result

    def get_metadata(self) -> Dict[str, Any]:
        """Get mock model metadata.
        
        Returns:
            Metadata dictionary
        """
        return {
            "type": "mock",
            "name": self.name,
            "delay": self.delay,
            "accuracy": self.accuracy,
            "prediction_count": self.prediction_count,
        }
