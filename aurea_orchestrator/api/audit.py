"""Audit API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from aurea_orchestrator.api.schemas import (
    AuditLogQueryRequest,
    AuditLogQueryResponse,
    AuditLogResponse,
)
from aurea_orchestrator.core.database import get_db_session
from aurea_orchestrator.core.audit_service import AuditService

router = APIRouter(prefix="/audit", tags=["audit"])


@router.post("/query", response_model=AuditLogQueryResponse)
async def query_audit_logs(
    query_params: AuditLogQueryRequest,
    db: Session = Depends(get_db_session),
):
    """
    Query audit logs with various filters.
    
    This endpoint allows you to search and filter audit logs based on:
    - User who performed the action
    - Action type
    - Resource type and ID
    - Status (success/failure)
    - OpenTelemetry trace ID for correlation
    - Time range
    
    Results are paginated and sorted by timestamp (most recent first).
    """
    # Query logs
    logs = AuditService.query_logs(
        db=db,
        user=query_params.user,
        action=query_params.action,
        resource_type=query_params.resource_type,
        resource_id=query_params.resource_id,
        status=query_params.status,
        trace_id=query_params.trace_id,
        start_time=query_params.start_time,
        end_time=query_params.end_time,
        limit=query_params.limit,
        offset=query_params.offset,
    )

    # Count total matching logs
    total = AuditService.count_logs(
        db=db,
        user=query_params.user,
        action=query_params.action,
        resource_type=query_params.resource_type,
        status=query_params.status,
        trace_id=query_params.trace_id,
        start_time=query_params.start_time,
        end_time=query_params.end_time,
    )

    # Convert to response schema
    log_responses = [AuditLogResponse.model_validate(log) for log in logs]

    return AuditLogQueryResponse(
        total=total,
        limit=query_params.limit,
        offset=query_params.offset,
        logs=log_responses,
    )


@router.get("/query", response_model=AuditLogQueryResponse)
async def query_audit_logs_get(
    user: Optional[str] = Query(None, description="Filter by user"),
    action: Optional[str] = Query(None, description="Filter by action"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    resource_id: Optional[str] = Query(None, description="Filter by resource ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    trace_id: Optional[str] = Query(None, description="Filter by trace ID"),
    start_time: Optional[datetime] = Query(None, description="Filter by start time (ISO 8601)"),
    end_time: Optional[datetime] = Query(None, description="Filter by end time (ISO 8601)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: Session = Depends(get_db_session),
):
    """
    Query audit logs with various filters (GET method).
    
    This is an alternative GET endpoint for querying audit logs.
    For complex queries, use the POST /audit/query endpoint instead.
    """
    query_params = AuditLogQueryRequest(
        user=user,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        status=status,
        trace_id=trace_id,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        offset=offset,
    )
    
    return await query_audit_logs(query_params, db)


@router.get("/{log_id}", response_model=AuditLogResponse)
async def get_audit_log(
    log_id: int,
    db: Session = Depends(get_db_session),
):
    """Get a specific audit log by ID."""
    log = AuditService.get_log_by_id(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Audit log not found")
    
    return AuditLogResponse.model_validate(log)
