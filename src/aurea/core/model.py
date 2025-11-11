"""Base model interface for Aurea orchestrator."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class Model(ABC):
    """Abstract base class for models."""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """Initialize the model.
        
        Args:
            name: Name of the model
            config: Optional configuration dictionary
        """
        self.name = name
        self.config = config or {}

    @abstractmethod
    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a prediction.
        
        Args:
            input_data: Input data for prediction
            
        Returns:
            Prediction results
        """
        pass

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Get model metadata.
        
        Returns:
            Dictionary containing model metadata
        """
        pass
