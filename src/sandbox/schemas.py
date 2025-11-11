"""Pydantic models for API request/response schemas."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List


class TestRunSpec(BaseModel):
    """Specification for a test run in the sandbox."""
    
    code: str = Field(..., description="The code to execute")
    language: str = Field(default="python", description="Programming language")
    timeout: Optional[int] = Field(
        default=None,
        ge=1,
        le=300,
        description="Execution timeout in seconds (1-300)"
    )
    files: Optional[Dict[str, str]] = Field(
        default=None,
        description="Additional files to include {filename: content}"
    )
    readonly: bool = Field(
        default=True,
        description="Mount workspace as read-only"
    )
    capture_artifacts: bool = Field(
        default=True,
        description="Capture output files/artifacts"
    )


class TestRunResult(BaseModel):
    """Result of a test run execution."""
    
    run_id: str = Field(..., description="Unique identifier for this run")
    success: bool = Field(..., description="Whether execution succeeded")
    exit_code: int = Field(..., description="Process exit code")
    stdout: str = Field(..., description="Standard output")
    stderr: str = Field(..., description="Standard error")
    execution_time: float = Field(..., description="Execution time in seconds")
    timed_out: bool = Field(..., description="Whether execution timed out")
    timeout: int = Field(..., description="Timeout used for execution")
    artifacts: Dict[str, str] = Field(
        default_factory=dict,
        description="Captured artifacts {filename: content}"
    )


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str = Field(..., description="Service status")
    sandbox_available: bool = Field(..., description="Whether sandbox is available")
    docker_version: Optional[str] = Field(None, description="Docker version")
