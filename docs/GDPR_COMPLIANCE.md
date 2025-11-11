# GDPR Compliance Documentation

## Overview

The Aurea Orchestrator implements comprehensive GDPR (General Data Protection Regulation) compliance features to ensure proper handling of personal data and protection of individual rights.

## GDPR Principles Implementation

### 1. Lawfulness, Fairness, and Transparency (Article 5.1.a)

**Implementation:**
- Consent logging system tracks all user consent decisions with timestamps
- API endpoint: `POST /compliance/consent` records user consent
- Each consent includes type, granted status, IP address, and metadata
- Full audit trail available via `GET /compliance/consent/{user_id}`

**Usage Example:**
```json
POST /compliance/consent
{
  "user_id": "user123",
  "consent_type": "data_processing",
  "granted": true,
  "ip_address": "192.168.1.1"
}
```

### 2. Purpose Limitation (Article 5.1.b)

**Implementation:**
- Consent types specify exact purposes (e.g., "data_processing", "analytics", "marketing")
- Each PII record includes metadata describing collection purpose
- Audit logs track how data is used in model inputs/outputs

### 3. Data Minimization (Article 5.1.c)

**Implementation:**
- Anonymization service automatically reduces PII to minimum necessary
- Configurable retention periods (default: 90 days)
- Automated purging of old data via `POST /data/purge`

**Anonymization Methods:**
- Email: `john.doe@example.com` → `j***e@***.com`
- Name: `John Smith` → `J. S.`
- Phone: `555-123-4567` → `***-***-4567`
- SSN: `123-45-6789` → `***-**-6789`

### 4. Accuracy (Article 5.1.d)

**Implementation:**
- Last accessed timestamps track data currency
- PII records include creation and access dates
- Regular purging ensures outdated data is removed

### 5. Storage Limitation (Article 5.1.e)

**Implementation:**
- Configurable retention policies in `config.json`
- Default retention: 90 days for PII
- Automated purging endpoint: `POST /data/purge`

**Purge Types:**
- `pii`: Remove old PII records
- `audit`: Remove old audit logs
- `consent`: Remove old consent records
- `all`: Comprehensive data cleanup

**Usage Example:**
```json
POST /data/purge
{
  "purge_type": "pii",
  "retention_days": 90,
  "dry_run": false
}
```

### 6. Integrity and Confidentiality (Article 5.1.f)

**Implementation:**
- PII encryption using Fernet (symmetric encryption)
- Encrypted storage of all sensitive data
- Anonymization before data exposure
- Secure API with potential for authentication middleware

## Individual Rights (Chapter III)

### Right to Access (Article 15)

**Endpoints:**
- `GET /compliance/consent/{user_id}` - Access consent history
- `GET /compliance/audit?user_id={user_id}` - Access audit trail

### Right to Rectification (Article 16)

**Implementation:**
- PII records can be updated through database operations
- Audit logs track all changes

### Right to Erasure (Article 17)

**Endpoints:**
- `POST /data/purge` - Delete old data
- `POST /data/anonymize/{user_id}` - Anonymize user data

**Usage Example:**
```bash
POST /data/anonymize/user123
```

This anonymizes all PII for the specified user while maintaining audit trail.

### Right to Data Portability (Article 20)

**Implementation:**
- All data accessible via API in structured JSON format
- Export user data via GET endpoints

## Record-Keeping (Article 30)

**Implementation:**
- Comprehensive compliance reports via `GET /compliance/report`
- Reports include:
  - Total PII records
  - Anonymized records count
  - Active consents
  - Audit log statistics
  - Purge history

**Report Example:**
```json
{
  "total_pii_records": 1500,
  "anonymized_records": 250,
  "active_consents": 1200,
  "total_audit_logs": 5000,
  "records_pending_purge": 100,
  "oldest_pii_record": "2025-08-11T10:30:00",
  "newest_pii_record": "2025-11-11T08:45:00",
  "purge_history": [...]
}
```

## Data Protection Impact Assessment (DPIA)

### When to Conduct DPIA

Conduct DPIA when:
- Processing large volumes of PII
- Using automated decision-making
- Processing special categories of data
- Systematic monitoring

### DPIA Considerations

1. **Data Types**: Email, name, phone, SSN, address
2. **Processing Activities**: Model inference, analytics
3. **Risks**: Unauthorized access, data breach
4. **Safeguards**: Encryption, anonymization, access controls
5. **Retention**: Automated purging after retention period

## Breach Notification (Articles 33-34)

### Detection
- Monitor audit logs for unusual activity
- Review compliance reports regularly
- Track failed authentication attempts (if implemented)

### Response Procedure
1. Identify affected data via audit logs
2. Generate compliance report
3. Notify authorities within 72 hours
4. Notify affected individuals if high risk
5. Document breach in audit log

## Data Processing Agreement (DPA)

For processors handling data on behalf of controllers:

### Controller Obligations
- Define processing purposes
- Ensure lawful basis for processing
- Implement appropriate security measures

### Processor Obligations
- Process data only on documented instructions
- Ensure confidentiality of personnel
- Implement technical and organizational measures
- Assist with DSAR (Data Subject Access Requests)
- Delete or return data after service termination

## Configuration

Edit `config.json` to customize compliance settings:

```json
{
  "compliance": {
    "pii_retention_days": 90,
    "anonymization": {
      "enabled": true,
      "fields": ["email", "name", "phone", "ssn", "address"]
    },
    "audit_logging": {
      "enabled": true,
      "log_model_inputs": true,
      "log_model_outputs": true
    }
  }
}
```

## Compliance Checklist

- [x] Lawful basis for processing (consent)
- [x] Data minimization (anonymization)
- [x] Storage limitation (automated purging)
- [x] Security measures (encryption)
- [x] Individual rights (access, erasure, portability)
- [x] Record-keeping (audit logs, reports)
- [x] Breach detection (audit monitoring)
- [x] Data protection by design
- [x] Data protection by default

## Audit and Monitoring

### Regular Reviews
- Weekly: Review compliance reports
- Monthly: Execute dry-run purges
- Quarterly: Full compliance audit
- Annually: DPIA review and update

### Monitoring Commands
```bash
# Check compliance status
GET /compliance/report

# Preview purge candidates
POST /data/purge {"purge_type": "all", "dry_run": true}

# Review recent audit logs
GET /compliance/audit?limit=100
```

## Contact

For GDPR inquiries or data subject requests:
- Email: dpo@aurea-orchestrator.example.com (configure for your organization)
- API: Use provided endpoints for automated requests
