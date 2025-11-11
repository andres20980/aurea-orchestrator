"""Pydantic schemas for API requests and responses."""

from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field


class AuditLogResponse(BaseModel):
    """Response schema for audit log."""
    
    id: int
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    timestamp: datetime
    user: str
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    before_state: Optional[str] = None
    after_state: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    metadata: Optional[str] = None

    class Config:
        from_attributes = True


class AuditLogQueryRequest(BaseModel):
    """Request schema for querying audit logs."""
    
    user: Optional[str] = Field(None, description="Filter by user")
    action: Optional[str] = Field(None, description="Filter by action")
    resource_type: Optional[str] = Field(None, description="Filter by resource type")
    resource_id: Optional[str] = Field(None, description="Filter by resource ID")
    status: Optional[str] = Field(None, description="Filter by status (success/failure)")
    trace_id: Optional[str] = Field(None, description="Filter by OpenTelemetry trace ID")
    start_time: Optional[datetime] = Field(None, description="Filter by start time (ISO 8601)")
    end_time: Optional[datetime] = Field(None, description="Filter by end time (ISO 8601)")
    limit: int = Field(100, ge=1, le=1000, description="Maximum number of results (1-1000)")
    offset: int = Field(0, ge=0, description="Number of results to skip")


class AuditLogQueryResponse(BaseModel):
    """Response schema for audit log query."""
    
    total: int = Field(..., description="Total number of matching logs")
    limit: int = Field(..., description="Limit applied to query")
    offset: int = Field(..., description="Offset applied to query")
    logs: list[AuditLogResponse] = Field(..., description="List of audit logs")


class ActionRequest(BaseModel):
    """Example request for an action that should be audited."""
    
    name: str = Field(..., description="Name of the resource")
    description: Optional[str] = Field(None, description="Description")
    tags: Optional[list[str]] = Field(default_factory=list, description="Tags")


class ActionResponse(BaseModel):
    """Example response for an action."""
    
    id: str
    name: str
    description: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    created_at: datetime
    created_by: str
