"""Data models for the orchestrator."""
from enum import Enum
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """Status of a job."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    APPROVED = "approved"
    REJECTED = "rejected"


class ReviewFeedback(BaseModel):
    """Review feedback for a completed job."""
    reviewer: str
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating from 1-5")
    comments: Optional[str] = None
    approved: bool
    reviewed_at: datetime = Field(default_factory=datetime.utcnow)


class Job(BaseModel):
    """A job in the orchestrator system."""
    id: str
    prompt: str
    solution: Optional[str] = None
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    review_feedback: Optional[ReviewFeedback] = None
    metadata: Optional[dict] = Field(default_factory=dict)


class TrainingExample(BaseModel):
    """Training data format for LLM fine-tuning."""
    prompt: str
    solution: str
    feedback: Optional[dict] = None
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "prompt": "Write a function to calculate factorial",
                "solution": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)",
                "feedback": {
                    "reviewer": "john_doe",
                    "rating": 5,
                    "comments": "Well implemented with proper base case",
                    "approved": True
                }
            }
        }
