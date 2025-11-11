from typing import TypedDict, Literal, Optional, List
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    """Status of the overall job"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class NodeStatus(str, Enum):
    """Status of individual nodes in the workflow"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ReviewDecision(str, Enum):
    """Review decision outcomes"""
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING = "pending"


class NodeProgress(TypedDict):
    """Progress information for a single node"""
    node_name: str
    status: NodeStatus
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    output: Optional[str]
    error: Optional[str]


class WorkflowState(TypedDict):
    """State managed by the LangGraph workflow"""
    job_id: str
    input_data: dict
    plan_output: Optional[str]
    implement_output: Optional[str]
    test_output: Optional[str]
    review_precheck_output: Optional[str]
    review_output: Optional[str]
    review_decision: ReviewDecision
    iteration_count: int
    max_iterations: int
    node_progress: List[NodeProgress]
    current_node: Optional[str]
    error: Optional[str]


class JobRequest(TypedDict):
    """Request body for creating a new job"""
    input_data: dict
    max_iterations: Optional[int]


class JobResponse(TypedDict):
    """Response for job creation"""
    job_id: str
    status: JobStatus
    created_at: datetime


class JobStatusResponse(TypedDict):
    """Response for job status query"""
    job_id: str
    status: JobStatus
    current_node: Optional[str]
    iteration_count: int
    max_iterations: int
    node_progress: List[NodeProgress]
    created_at: datetime
    updated_at: datetime
