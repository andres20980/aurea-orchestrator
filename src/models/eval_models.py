"""Pydantic models for evaluation system"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum


class FeatureType(str, Enum):
    """Types of agent features to evaluate"""
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    DEBUGGING = "debugging"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    REFACTORING = "refactoring"


class EvalCase(BaseModel):
    """Represents a single evaluation test case"""
    case_id: str = Field(..., description="Unique identifier for the test case")
    feature_type: FeatureType = Field(..., description="Feature being tested")
    test_type: str = Field(..., description="Type of test (golden/regression)")
    description: str = Field(..., description="Human-readable description")
    input_data: Dict[str, Any] = Field(..., description="Input for the agent")
    expected_output: Dict[str, Any] = Field(..., description="Expected result")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "case_id": "code_gen_001",
                "feature_type": "code_generation",
                "test_type": "golden",
                "description": "Generate a simple function",
                "input_data": {"prompt": "Create a function to add two numbers"},
                "expected_output": {"contains": ["def", "add", "return"]},
                "metadata": {"difficulty": "easy"}
            }
        }


class EvalScore(BaseModel):
    """Scorecard metrics for an evaluation"""
    accuracy: float = Field(..., ge=0.0, le=1.0, description="Accuracy score (0-1)")
    latency_ms: float = Field(..., ge=0.0, description="Latency in milliseconds")
    cost: float = Field(..., ge=0.0, description="Cost in USD")
    passed: bool = Field(..., description="Whether the test passed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "accuracy": 0.95,
                "latency_ms": 1234.56,
                "cost": 0.0025,
                "passed": True
            }
        }


class EvalResultResponse(BaseModel):
    """Response for a single evaluation result"""
    case_id: str
    feature_type: str
    test_type: str
    passed: bool
    accuracy: Optional[float] = None
    latency_ms: Optional[float] = None
    cost: Optional[float] = None
    error_message: Optional[str] = None
    executed_at: datetime


class EvalRunRequest(BaseModel):
    """Request to run an evaluation suite"""
    feature_type: Optional[FeatureType] = Field(
        default=None, 
        description="Filter by feature type, or None for all"
    )
    test_type: Optional[str] = Field(
        default=None,
        description="Filter by test type (golden/regression), or None for all"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata for this run"
    )


class EvalRunResponse(BaseModel):
    """Response for an evaluation run"""
    run_id: str
    status: str
    feature_type: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_cases: int
    passed_cases: int
    failed_cases: int
    average_accuracy: Optional[float] = None
    average_latency: Optional[float] = None
    total_cost: Optional[float] = None
    results: Optional[List[EvalResultResponse]] = None
