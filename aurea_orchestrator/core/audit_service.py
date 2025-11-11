"""Audit logging service."""

import json
from datetime import datetime
from typing import Optional, Any, Dict
from sqlalchemy.orm import Session

from aurea_orchestrator.models.audit import AuditLog
from aurea_orchestrator.core.tracing import get_current_trace_id, get_current_span_id


class AuditService:
    """Service for creating and managing audit logs."""

    @staticmethod
    def log_action(
        db: Session,
        user: str,
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        before_state: Optional[Dict[str, Any]] = None,
        after_state: Optional[Dict[str, Any]] = None,
        status: str = "success",
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
    ) -> AuditLog:
        """
        Log an action to the audit log.

        Args:
            db: Database session
            user: User who performed the action
            action: Action performed (e.g., "create_resource", "update_config")
            resource_type: Type of resource affected (e.g., "workflow", "task")
            resource_id: ID of the affected resource
            before_state: State before the action (will be JSON serialized)
            after_state: State after the action (will be JSON serialized)
            status: Action status ("success" or "failure")
            error_message: Error message if action failed
            metadata: Additional metadata (will be JSON serialized)
            trace_id: OpenTelemetry trace ID (auto-detected if not provided)
            span_id: OpenTelemetry span ID (auto-detected if not provided)

        Returns:
            Created AuditLog instance
        """
        # Auto-detect trace and span IDs if not provided
        if trace_id is None:
            trace_id = get_current_trace_id()
        if span_id is None:
            span_id = get_current_span_id()

        # Serialize complex objects to JSON
        before_json = json.dumps(before_state) if before_state else None
        after_json = json.dumps(after_state) if after_state else None
        metadata_json = json.dumps(metadata) if metadata else None

        # Create audit log entry
        audit_log = AuditLog(
            trace_id=trace_id,
            span_id=span_id,
            timestamp=datetime.utcnow(),
            user=user,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            before_state=before_json,
            after_state=after_json,
            status=status,
            error_message=error_message,
            metadata=metadata_json,
        )

        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)

        return audit_log

    @staticmethod
    def query_logs(
        db: Session,
        user: Optional[str] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        status: Optional[str] = None,
        trace_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AuditLog]:
        """
        Query audit logs with filters.

        Args:
            db: Database session
            user: Filter by user
            action: Filter by action
            resource_type: Filter by resource type
            resource_id: Filter by resource ID
            status: Filter by status
            trace_id: Filter by trace ID
            start_time: Filter by start time (inclusive)
            end_time: Filter by end time (inclusive)
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of matching AuditLog instances
        """
        query = db.query(AuditLog)

        # Apply filters
        if user:
            query = query.filter(AuditLog.user == user)
        if action:
            query = query.filter(AuditLog.action == action)
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        if resource_id:
            query = query.filter(AuditLog.resource_id == resource_id)
        if status:
            query = query.filter(AuditLog.status == status)
        if trace_id:
            query = query.filter(AuditLog.trace_id == trace_id)
        if start_time:
            query = query.filter(AuditLog.timestamp >= start_time)
        if end_time:
            query = query.filter(AuditLog.timestamp <= end_time)

        # Order by timestamp descending (most recent first)
        query = query.order_by(AuditLog.timestamp.desc())

        # Apply pagination
        query = query.limit(limit).offset(offset)

        return query.all()

    @staticmethod
    def get_log_by_id(db: Session, log_id: int) -> Optional[AuditLog]:
        """Get a specific audit log by ID."""
        return db.query(AuditLog).filter(AuditLog.id == log_id).first()

    @staticmethod
    def count_logs(
        db: Session,
        user: Optional[str] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        status: Optional[str] = None,
        trace_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> int:
        """
        Count audit logs matching the filters.

        Args:
            db: Database session
            user: Filter by user
            action: Filter by action
            resource_type: Filter by resource type
            status: Filter by status
            trace_id: Filter by trace ID
            start_time: Filter by start time (inclusive)
            end_time: Filter by end time (inclusive)

        Returns:
            Count of matching audit logs
        """
        query = db.query(AuditLog)

        # Apply filters
        if user:
            query = query.filter(AuditLog.user == user)
        if action:
            query = query.filter(AuditLog.action == action)
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        if status:
            query = query.filter(AuditLog.status == status)
        if trace_id:
            query = query.filter(AuditLog.trace_id == trace_id)
        if start_time:
            query = query.filter(AuditLog.timestamp >= start_time)
        if end_time:
            query = query.filter(AuditLog.timestamp <= end_time)

        return query.count()
