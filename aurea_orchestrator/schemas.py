"""Schemas for Aurea Orchestrator."""

from enum import Enum
from typing import Any

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
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowState(BaseModel):
    """State of the workflow."""

    task_id: str
    task_description: str
    status: TaskStatus = TaskStatus.PENDING
    context: str | None = None
    architecture: str | None = None
    code: str | None = None
    tests: str | None = None
    review: str | None = None
    messages: list[AgentMessage] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TaskRequest(BaseModel):
    """Request to create a new task."""

    description: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class TaskResponse(BaseModel):
    """Response with task information."""

    task_id: str
    status: TaskStatus
    result: dict[str, Any] | None = None
