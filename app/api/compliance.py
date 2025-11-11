"""
Compliance API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import json
import os

from app.database import get_db
from app.models.schemas import (
    ConsentRequest, ConsentResponse,
    AuditRequest, AuditResponse,
    ComplianceReport, PurgeRequest, PurgeResponse
)
from app.services import AnonymizationService, ComplianceService

router = APIRouter(prefix="/compliance", tags=["compliance"])

# Load config for default retention days
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config.json")
with open(config_path, "r") as f:
    config = json.load(f)

DEFAULT_RETENTION_DAYS = config["compliance"]["pii_retention_days"]


def get_compliance_service(db: Session = Depends(get_db)) -> ComplianceService:
    """Dependency for compliance service"""
    anonymizer = AnonymizationService()
    return ComplianceService(db, anonymizer)


@router.post("/consent", response_model=ConsentResponse)
async def log_consent(
    request: ConsentRequest,
    service: ComplianceService = Depends(get_compliance_service)
):
    """
    Log user consent for data processing
    
    This endpoint records user consent decisions for GDPR compliance.
    """
    consent = service.log_consent(
        user_id=request.user_id,
        consent_type=request.consent_type,
        granted=request.granted,
        ip_address=request.ip_address,
        metadata=request.metadata
    )
    return consent


@router.get("/consent/{user_id}")
async def get_user_consents(
    user_id: str,
    service: ComplianceService = Depends(get_compliance_service)
):
    """
    Get all consent records for a user
    
    Returns the complete consent history for audit purposes.
    """
    consents = service.get_user_consents(user_id)
    return {"user_id": user_id, "consents": consents}


@router.post("/audit", response_model=AuditResponse)
async def log_audit(
    request: AuditRequest,
    service: ComplianceService = Depends(get_compliance_service)
):
    """
    Log model input/output for audit trail
    
    Records model inference requests and responses for compliance auditing.
    """
    audit = service.log_audit(
        model_name=request.model_name,
        input_data=request.input_data,
        output_data=request.output_data,
        user_id=request.user_id,
        execution_time_ms=request.execution_time_ms,
        status=request.status,
        metadata=request.metadata
    )
    return audit


@router.get("/audit")
async def get_audit_logs(
    user_id: Optional[str] = None,
    model_name: Optional[str] = None,
    limit: int = 100,
    service: ComplianceService = Depends(get_compliance_service)
):
    """
    Retrieve audit logs with optional filters
    
    Supports filtering by user_id and/or model_name.
    """
    logs = service.get_audit_logs(user_id=user_id, model_name=model_name, limit=limit)
    return {"count": len(logs), "logs": logs}


@router.get("/report", response_model=ComplianceReport)
async def get_compliance_report(
    service: ComplianceService = Depends(get_compliance_service)
):
    """
    Generate comprehensive compliance report
    
    Provides overview of:
    - PII records (total, anonymized, pending purge)
    - Consent logs (active consents)
    - Audit logs (total records)
    - Data purge history
    
    Essential for GDPR Article 30 record-keeping requirements.
    """
    report = service.generate_compliance_report()
    return report
