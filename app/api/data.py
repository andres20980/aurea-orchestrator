"""
Data management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
import os

from app.database import get_db
from app.models.schemas import PurgeRequest, PurgeResponse
from app.services import AnonymizationService, ComplianceService

router = APIRouter(prefix="/data", tags=["data"])

# Load config for default retention days
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config.json")
with open(config_path, "r") as f:
    config = json.load(f)

DEFAULT_RETENTION_DAYS = config["compliance"]["pii_retention_days"]


def get_compliance_service(db: Session = Depends(get_db)) -> ComplianceService:
    """Dependency for compliance service"""
    anonymizer = AnonymizationService()
    return ComplianceService(db, anonymizer)


@router.post("/purge", response_model=PurgeResponse)
async def purge_data(
    request: PurgeRequest,
    service: ComplianceService = Depends(get_compliance_service)
):
    """
    Purge old data according to retention policies
    
    Supported purge types:
    - 'pii': Purge old PII records
    - 'audit': Purge old audit logs
    - 'consent': Purge old consent logs
    - 'all': Purge all old data
    
    Uses default retention period from config unless overridden.
    Set dry_run=true to preview what would be deleted.
    
    Required for GDPR Article 17 (Right to Erasure) and data minimization.
    """
    if request.purge_type not in ["pii", "audit", "consent", "all"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid purge_type. Must be one of: pii, audit, consent, all"
        )
    
    retention_days = request.retention_days or DEFAULT_RETENTION_DAYS
    
    purge_log = service.purge_old_data(
        purge_type=request.purge_type,
        retention_days=retention_days,
        dry_run=request.dry_run
    )
    
    return PurgeResponse(
        purge_id=purge_log.id,
        purge_type=purge_log.purge_type,
        records_deleted=purge_log.records_deleted,
        retention_days=purge_log.retention_days,
        timestamp=purge_log.timestamp,
        dry_run=request.dry_run
    )


@router.post("/anonymize/{user_id}")
async def anonymize_user_data(
    user_id: str,
    service: ComplianceService = Depends(get_compliance_service),
    db: Session = Depends(get_db)
):
    """
    Anonymize all PII for a specific user
    
    Implements the right to anonymization under GDPR.
    """
    from app.models.database import PIIRecord
    
    pii_records = db.query(PIIRecord).filter(
        PIIRecord.user_id == user_id,
        PIIRecord.anonymized == False
    ).all()
    
    anonymized_count = 0
    for pii in pii_records:
        if service.anonymize_pii(pii.id):
            anonymized_count += 1
    
    return {
        "user_id": user_id,
        "records_anonymized": anonymized_count,
        "status": "completed"
    }
