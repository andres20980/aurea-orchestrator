# Aurea Orchestrator

**Automated Unified Reasoning & Execution Agents with Data Compliance Layer**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![GDPR Compliant](https://img.shields.io/badge/GDPR-Compliant-success.svg)](docs/GDPR_COMPLIANCE.md)
[![SOC2 Ready](https://img.shields.io/badge/SOC2-Ready-success.svg)](docs/SOC2_COMPLIANCE.md)

A comprehensive data compliance layer for AI/ML orchestration systems, implementing GDPR and SOC2 requirements including data anonymization, consent management, audit logging, and automated data purging.

## Features

✅ **Data Anonymization** - Automatic PII anonymization with field-specific algorithms  
✅ **Consent Management** - Complete consent logging and tracking system  
✅ **Audit Logging** - Comprehensive audit trail for model inputs/outputs  
✅ **Data Purging** - Automated retention policies and data deletion  
✅ **Compliance Reporting** - Real-time compliance status and metrics  
✅ **GDPR Compliance** - Full implementation of GDPR requirements  
✅ **SOC2 Ready** - Trust Services Criteria implementation  

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/andres20980/aurea-orchestrator.git
cd aurea-orchestrator

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

The API will be available at `http://localhost:8000`

### API Documentation

Once running, access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Compliance Endpoints

#### Log User Consent
```bash
POST /compliance/consent
{
  "user_id": "user123",
  "consent_type": "data_processing",
  "granted": true,
  "ip_address": "192.168.1.1"
}
```

#### Get User Consents
```bash
GET /compliance/consent/{user_id}
```

#### Log Audit Trail
```bash
POST /compliance/audit
{
  "model_name": "classifier",
  "input_data": "sample input",
  "output_data": "sample output",
  "user_id": "user123",
  "status": "success"
}
```

#### Get Audit Logs
```bash
GET /compliance/audit?user_id=user123&limit=100
```

#### Get Compliance Report
```bash
GET /compliance/report
```

**Response:**
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

### Data Management Endpoints

#### Purge Old Data
```bash
POST /data/purge
{
  "purge_type": "pii",  # Options: pii, audit, consent, all
  "retention_days": 90,
  "dry_run": false
}
```

#### Anonymize User Data
```bash
POST /data/anonymize/{user_id}
```

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

## Data Anonymization

The system supports automatic anonymization for various PII types:

| Data Type | Example | Anonymized |
|-----------|---------|------------|
| Email | john.doe@example.com | j***e@***.com |
| Name | John Smith | J. S. |
| Phone | 555-123-4567 | ***-***-4567 |
| SSN | 123-45-6789 | ***-**-6789 |
| Address | 123 Main St, City | ***, City |

## Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

## Compliance Documentation

Comprehensive compliance documentation is available:

- **[GDPR Compliance](docs/GDPR_COMPLIANCE.md)** - Complete GDPR implementation guide
- **[SOC2 Compliance](docs/SOC2_COMPLIANCE.md)** - SOC2 Trust Services Criteria

### GDPR Features

- ✅ Lawfulness, fairness, transparency (Article 5.1.a)
- ✅ Purpose limitation (Article 5.1.b)
- ✅ Data minimization (Article 5.1.c)
- ✅ Accuracy (Article 5.1.d)
- ✅ Storage limitation (Article 5.1.e)
- ✅ Integrity and confidentiality (Article 5.1.f)
- ✅ Right to access (Article 15)
- ✅ Right to erasure (Article 17)
- ✅ Right to data portability (Article 20)
- ✅ Record-keeping (Article 30)

### SOC2 Controls

- ✅ Security (Common Criteria)
- ✅ Availability monitoring
- ✅ Processing integrity
- ✅ Confidentiality safeguards
- ✅ Privacy controls

## Architecture

```
aurea-orchestrator/
├── app/
│   ├── models/          # Database and Pydantic models
│   ├── services/        # Business logic (anonymization, compliance)
│   ├── api/             # API endpoints
│   └── database.py      # Database configuration
├── docs/                # Compliance documentation
├── tests/               # Test suite
├── config.json          # Configuration
├── main.py              # Application entry point
└── requirements.txt     # Dependencies
```

## Development

### Project Structure

- **Models**: Database models and API schemas
- **Services**: Core business logic for compliance operations
- **API**: FastAPI routers and endpoints
- **Tests**: Comprehensive test coverage

### Adding New Features

1. Define models in `app/models/`
2. Implement business logic in `app/services/`
3. Create API endpoints in `app/api/`
4. Add tests in `tests/`
5. Update documentation

## Security

- **Encryption**: Fernet symmetric encryption for PII
- **Anonymization**: Field-specific algorithms
- **Audit Trail**: Complete logging of all operations
- **Access Control**: Ready for authentication middleware

## Monitoring

### Health Checks

```bash
GET /health
```

### Compliance Monitoring

```bash
# Daily
GET /health

# Weekly
GET /compliance/report

# Monthly
POST /data/purge {"purge_type": "all", "dry_run": true}
```

## License

MIT License - See LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For issues or questions:
- GitHub Issues: https://github.com/andres20980/aurea-orchestrator/issues
- Documentation: See `/docs` directory

## Roadmap

- [ ] JWT authentication
- [ ] Role-based access control (RBAC)
- [ ] Data export functionality
- [ ] Scheduled purge jobs
- [ ] Compliance dashboard UI
- [ ] Multi-tenancy support
- [ ] Advanced analytics

---

**Built with ❤️ for GDPR and SOC2 compliance**
