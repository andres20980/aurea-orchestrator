"""
Database models for compliance tracking
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ConsentLog(Base):
    """Track user consent for data processing"""
    __tablename__ = "consent_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    consent_type = Column(String, nullable=False)  # e.g., "data_processing", "analytics"
    granted = Column(Boolean, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    ip_address = Column(String, nullable=True)
    record_metadata = Column(JSON, nullable=True)


class PIIRecord(Base):
    """Track PII data for retention and purging"""
    __tablename__ = "pii_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    data_type = Column(String, nullable=False)  # e.g., "email", "name", "phone"
    encrypted_value = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_accessed = Column(DateTime, default=datetime.utcnow, nullable=False)
    anonymized = Column(Boolean, default=False)
    record_metadata = Column(JSON, nullable=True)


class AuditLog(Base):
    """Audit log for model inputs and outputs"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=True)
    model_name = Column(String, nullable=False)
    input_data = Column(Text, nullable=False)
    output_data = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    execution_time_ms = Column(Integer, nullable=True)
    status = Column(String, nullable=False)  # "success", "error"
    record_metadata = Column(JSON, nullable=True)


class DataPurgeLog(Base):
    """Log data purge operations"""
    __tablename__ = "data_purge_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    purge_type = Column(String, nullable=False)  # "pii", "audit", "consent"
    records_deleted = Column(Integer, nullable=False)
    retention_days = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    initiated_by = Column(String, nullable=True)
    record_metadata = Column(JSON, nullable=True)
