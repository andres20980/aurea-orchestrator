"""Schemas for Aurea Orchestrator."""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AgentType(str, Enum):
    """Types of agents in the system."""

    CONTEXT = "context"
    ARCHITECT = "architect"
    CODE = "code"
    TEST = "test"
    REVIEW = "review"


class TaskStatus(str, Enum):
    """Status of a task."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentMessage(BaseModel):
    """Message passed between agents."""

    agent_type: AgentType
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkflowState(BaseModel):
    """State of the workflow."""

    task_id: str
    task_description: str
    status: TaskStatus = TaskStatus.PENDING
    context: Optional[str] = None
    architecture: Optional[str] = None
    code: Optional[str] = None
    tests: Optional[str] = None
    review: Optional[str] = None
    messages: List[AgentMessage] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TaskRequest(BaseModel):
    """Request to create a new task."""

    description: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TaskResponse(BaseModel):
    """Response with task information."""

    task_id: str
    status: TaskStatus
    result: Optional[Dict[str, Any]] = None
