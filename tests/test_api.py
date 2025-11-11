"""
Tests for compliance API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from app.database import get_db
from app.models.database import Base

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """Create and drop test database for each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Aurea Orchestrator"
    assert data["compliance"]["gdpr_compliant"] is True


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_log_consent():
    """Test consent logging"""
    consent_data = {
        "user_id": "user123",
        "consent_type": "data_processing",
        "granted": True,
        "ip_address": "192.168.1.1"
    }
    
    response = client.post("/compliance/consent", json=consent_data)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "user123"
    assert data["consent_type"] == "data_processing"
    assert data["granted"] is True


def test_get_user_consents():
    """Test retrieving user consents"""
    # First, log a consent
    consent_data = {
        "user_id": "user456",
        "consent_type": "analytics",
        "granted": True
    }
    client.post("/compliance/consent", json=consent_data)
    
    # Retrieve consents
    response = client.get("/compliance/consent/user456")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "user456"
    assert len(data["consents"]) == 1


def test_log_audit():
    """Test audit logging"""
    audit_data = {
        "model_name": "classifier",
        "input_data": "test input",
        "output_data": "test output",
        "user_id": "user789",
        "execution_time_ms": 150,
        "status": "success"
    }
    
    response = client.post("/compliance/audit", json=audit_data)
    assert response.status_code == 200
    data = response.json()
    assert data["model_name"] == "classifier"
    assert data["status"] == "success"


def test_get_audit_logs():
    """Test retrieving audit logs"""
    # Log an audit entry
    audit_data = {
        "model_name": "detector",
        "input_data": "sample data",
        "status": "success"
    }
    client.post("/compliance/audit", json=audit_data)
    
    # Retrieve audit logs
    response = client.get("/compliance/audit")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 1


def test_compliance_report():
    """Test compliance report generation"""
    response = client.get("/compliance/report")
    assert response.status_code == 200
    data = response.json()
    assert "total_pii_records" in data
    assert "anonymized_records" in data
    assert "active_consents" in data
    assert "total_audit_logs" in data


def test_purge_data_dry_run():
    """Test data purge dry run"""
    purge_data = {
        "purge_type": "all",
        "retention_days": 90,
        "dry_run": True
    }
    
    response = client.post("/data/purge", json=purge_data)
    assert response.status_code == 200
    data = response.json()
    assert data["purge_type"] == "all"
    assert data["dry_run"] is True


def test_purge_data_invalid_type():
    """Test data purge with invalid type"""
    purge_data = {
        "purge_type": "invalid",
        "dry_run": True
    }
    
    response = client.post("/data/purge", json=purge_data)
    assert response.status_code == 400


def test_anonymize_user_data():
    """Test user data anonymization"""
    # Note: This test requires PII records to exist
    response = client.post("/data/anonymize/user999")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "user999"
    assert "records_anonymized" in data
