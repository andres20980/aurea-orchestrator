"""
Pydantic models for API requests and responses
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict


class ConsentRequest(BaseModel):
    user_id: str
    consent_type: str
    granted: bool
    ip_address: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ConsentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: str
    consent_type: str
    granted: bool
    timestamp: datetime


class AuditRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    user_id: Optional[str] = None
    model_name: str
    input_data: str
    output_data: Optional[str] = None
    execution_time_ms: Optional[int] = None
    status: str = "success"
    metadata: Optional[Dict[str, Any]] = None


class AuditResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())
    
    id: int
    user_id: Optional[str]
    model_name: str
    timestamp: datetime
    status: str


class ComplianceReport(BaseModel):
    total_pii_records: int
    anonymized_records: int
    active_consents: int
    total_audit_logs: int
    records_pending_purge: int
    oldest_pii_record: Optional[datetime]
    newest_pii_record: Optional[datetime]
    purge_history: List[Dict[str, Any]]


class PurgeRequest(BaseModel):
    purge_type: str = Field(..., description="Type of data to purge: 'pii', 'audit', 'all'")
    retention_days: Optional[int] = Field(None, description="Override default retention period")
    dry_run: bool = Field(False, description="Preview what would be deleted without actually deleting")


class PurgeResponse(BaseModel):
    purge_id: int
    purge_type: str
    records_deleted: int
    retention_days: int
    timestamp: datetime
    dry_run: bool
