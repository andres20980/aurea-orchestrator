"""
Compliance service for managing consents, audits, and data purging
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.database import ConsentLog, PIIRecord, AuditLog, DataPurgeLog
from app.services.anonymization import AnonymizationService


class ComplianceService:
    """Service for managing compliance operations"""
    
    def __init__(self, db: Session, anonymization_service: AnonymizationService):
        self.db = db
        self.anonymizer = anonymization_service
    
    # Consent Management
    def log_consent(self, user_id: str, consent_type: str, granted: bool,
                   ip_address: Optional[str] = None, metadata: Optional[Dict] = None) -> ConsentLog:
        """Log user consent"""
        consent = ConsentLog(
            user_id=user_id,
            consent_type=consent_type,
            granted=granted,
            ip_address=ip_address,
            record_metadata=metadata
        )
        self.db.add(consent)
        self.db.commit()
        self.db.refresh(consent)
        return consent
    
    def get_user_consents(self, user_id: str) -> List[ConsentLog]:
        """Get all consents for a user"""
        return self.db.query(ConsentLog).filter(ConsentLog.user_id == user_id).all()
    
    def has_consent(self, user_id: str, consent_type: str) -> bool:
        """Check if user has granted consent"""
        latest = self.db.query(ConsentLog).filter(
            ConsentLog.user_id == user_id,
            ConsentLog.consent_type == consent_type
        ).order_by(ConsentLog.timestamp.desc()).first()
        
        return latest.granted if latest else False
    
    # PII Management
    def store_pii(self, user_id: str, data_type: str, value: str,
                 metadata: Optional[Dict] = None) -> PIIRecord:
        """Store PII data (encrypted)"""
        encrypted_value = self.anonymizer.encrypt_data(value)
        
        pii = PIIRecord(
            user_id=user_id,
            data_type=data_type,
            encrypted_value=encrypted_value,
            record_metadata=metadata
        )
        self.db.add(pii)
        self.db.commit()
        self.db.refresh(pii)
        return pii
    
    def anonymize_pii(self, pii_id: int) -> bool:
        """Anonymize a PII record"""
        pii = self.db.query(PIIRecord).filter(PIIRecord.id == pii_id).first()
        if not pii:
            return False
        
        # Decrypt, anonymize, re-encrypt
        original = self.anonymizer.decrypt_data(pii.encrypted_value)
        anonymized = self.anonymizer.anonymize_field(pii.data_type, original)
        pii.encrypted_value = self.anonymizer.encrypt_data(anonymized)
        pii.anonymized = True
        
        self.db.commit()
        return True
    
    def get_pii_for_purge(self, retention_days: int) -> List[PIIRecord]:
        """Get PII records older than retention period"""
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        return self.db.query(PIIRecord).filter(
            PIIRecord.created_at < cutoff_date
        ).all()
    
    # Audit Logging
    def log_audit(self, model_name: str, input_data: str, output_data: Optional[str] = None,
                 user_id: Optional[str] = None, execution_time_ms: Optional[int] = None,
                 status: str = "success", metadata: Optional[Dict] = None) -> AuditLog:
        """Log model input/output for audit"""
        audit = AuditLog(
            user_id=user_id,
            model_name=model_name,
            input_data=input_data,
            output_data=output_data,
            execution_time_ms=execution_time_ms,
            status=status,
            record_metadata=metadata
        )
        self.db.add(audit)
        self.db.commit()
        self.db.refresh(audit)
        return audit
    
    def get_audit_logs(self, user_id: Optional[str] = None, 
                      model_name: Optional[str] = None,
                      limit: int = 100) -> List[AuditLog]:
        """Get audit logs with optional filters"""
        query = self.db.query(AuditLog)
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if model_name:
            query = query.filter(AuditLog.model_name == model_name)
        
        return query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
    
    # Data Purging
    def purge_old_data(self, purge_type: str, retention_days: int,
                      initiated_by: Optional[str] = None, dry_run: bool = False) -> DataPurgeLog:
        """Purge old data based on retention policy"""
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        records_deleted = 0
        
        if purge_type in ["pii", "all"]:
            pii_query = self.db.query(PIIRecord).filter(PIIRecord.created_at < cutoff_date)
            records_deleted += pii_query.count()
            if not dry_run:
                pii_query.delete()
        
        if purge_type in ["audit", "all"]:
            audit_query = self.db.query(AuditLog).filter(AuditLog.timestamp < cutoff_date)
            records_deleted += audit_query.count()
            if not dry_run:
                audit_query.delete()
        
        if purge_type in ["consent", "all"]:
            consent_query = self.db.query(ConsentLog).filter(ConsentLog.timestamp < cutoff_date)
            records_deleted += consent_query.count()
            if not dry_run:
                consent_query.delete()
        
        # Log the purge operation
        purge_log = DataPurgeLog(
            purge_type=purge_type,
            records_deleted=records_deleted,
            retention_days=retention_days,
            initiated_by=initiated_by,
            record_metadata={"dry_run": dry_run}
        )
        self.db.add(purge_log)
        self.db.commit()
        self.db.refresh(purge_log)
        
        return purge_log
    
    # Compliance Reporting
    def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        # PII statistics
        total_pii = self.db.query(func.count(PIIRecord.id)).scalar()
        anonymized_pii = self.db.query(func.count(PIIRecord.id)).filter(
            PIIRecord.anonymized == True
        ).scalar()
        
        oldest_pii = self.db.query(func.min(PIIRecord.created_at)).scalar()
        newest_pii = self.db.query(func.max(PIIRecord.created_at)).scalar()
        
        # Consent statistics
        active_consents = self.db.query(func.count(ConsentLog.id)).filter(
            ConsentLog.granted == True
        ).scalar()
        
        # Audit statistics
        total_audits = self.db.query(func.count(AuditLog.id)).scalar()
        
        # Records pending purge (older than 90 days by default)
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        pending_purge = self.db.query(func.count(PIIRecord.id)).filter(
            PIIRecord.created_at < cutoff_date
        ).scalar()
        
        # Purge history
        purge_history = self.db.query(DataPurgeLog).order_by(
            DataPurgeLog.timestamp.desc()
        ).limit(10).all()
        
        return {
            "total_pii_records": total_pii or 0,
            "anonymized_records": anonymized_pii or 0,
            "active_consents": active_consents or 0,
            "total_audit_logs": total_audits or 0,
            "records_pending_purge": pending_purge or 0,
            "oldest_pii_record": oldest_pii,
            "newest_pii_record": newest_pii,
            "purge_history": [
                {
                    "id": log.id,
                    "purge_type": log.purge_type,
                    "records_deleted": log.records_deleted,
                    "retention_days": log.retention_days,
                    "timestamp": log.timestamp.isoformat() if log.timestamp else None
                }
                for log in purge_history
            ]
        }
