"""Database models for audit logging."""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, DateTime, Text, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AuditLog(Base):
    """Audit log model for tracking all system actions."""
    
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    trace_id = Column(String(32), index=True, nullable=True, doc="OpenTelemetry trace ID")
    span_id = Column(String(16), nullable=True, doc="OpenTelemetry span ID")
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    user = Column(String(255), index=True, nullable=False, doc="User who performed the action")
    action = Column(String(255), index=True, nullable=False, doc="Action performed")
    resource_type = Column(String(100), index=True, nullable=True, doc="Type of resource affected")
    resource_id = Column(String(255), index=True, nullable=True, doc="ID of resource affected")
    before_state = Column(Text, nullable=True, doc="State before action (JSON)")
    after_state = Column(Text, nullable=True, doc="State after action (JSON)")
    status = Column(String(50), index=True, default="success", doc="Action status (success/failure)")
    error_message = Column(Text, nullable=True, doc="Error message if action failed")
    metadata = Column(Text, nullable=True, doc="Additional metadata (JSON)")

    def __repr__(self):
        return f"<AuditLog(id={self.id}, user={self.user}, action={self.action}, timestamp={self.timestamp})>"
