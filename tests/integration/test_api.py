"""Integration tests for evaluation API"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from src.database.models import Base
from src.database import get_db

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function", autouse=True)
def test_db():
    """Create test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Create test client"""
    with TestClient(app) as test_client:
        yield test_client


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_run_evaluation_all(client):
    """Test running evaluation for all features"""
    response = client.post("/eval/run", json={})
    assert response.status_code == 200
    
    data = response.json()
    assert "run_id" in data
    assert data["status"] == "completed"
    assert data["total_cases"] > 0


def test_run_evaluation_by_feature(client):
    """Test running evaluation filtered by feature type"""
    response = client.post(
        "/eval/run",
        json={"feature_type": "code_generation"}
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["feature_type"] == "code_generation"
    assert data["total_cases"] > 0


def test_run_evaluation_by_test_type(client):
    """Test running evaluation filtered by test type"""
    response = client.post(
        "/eval/run",
        json={"test_type": "golden"}
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_cases"] > 0


def test_list_runs(client):
    """Test listing evaluation runs"""
    # First create a run
    client.post("/eval/run", json={})
    
    # Then list runs
    response = client.get("/eval/runs")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_run_details(client):
    """Test getting details of a specific run"""
    # Create a run
    create_response = client.post("/eval/run", json={})
    run_id = create_response.json()["run_id"]
    
    # Get run details
    response = client.get(f"/eval/runs/{run_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["run_id"] == run_id
    assert "results" in data


def test_get_run_not_found(client):
    """Test getting non-existent run"""
    response = client.get("/eval/runs/nonexistent")
    assert response.status_code == 404


def test_get_results(client):
    """Test getting results for a run"""
    # Create a run
    create_response = client.post("/eval/run", json={})
    run_id = create_response.json()["run_id"]
    
    # Get results
    response = client.get(f"/eval/results/{run_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    
    # Check result structure
    result = data[0]
    assert "case_id" in result
    assert "accuracy" in result
    assert "latency_ms" in result
    assert "cost" in result


def test_evaluation_metrics(client):
    """Test that evaluation includes all scorecard metrics"""
    response = client.post("/eval/run", json={})
    assert response.status_code == 200
    
    data = response.json()
    
    # Check aggregate metrics
    assert "average_accuracy" in data
    assert "average_latency" in data
    assert "total_cost" in data
    assert data["average_accuracy"] is not None
    assert data["average_latency"] is not None
    assert data["total_cost"] is not None
