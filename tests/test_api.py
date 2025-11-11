"""Tests for API endpoints."""
import pytest
from fastapi.testclient import TestClient
from app.main import app, router as model_router
import tempfile
import os


@pytest.fixture
def client():
    """Create test client."""
    # Use temporary files for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        metrics_file = os.path.join(tmpdir, "test_metrics.json")
        weights_file = os.path.join(tmpdir, "test_weights.json")
        
        # Reset router with temp files
        from app.router import ModelRouter
        new_router = ModelRouter(metrics_file=metrics_file, weights_file=weights_file)
        app.dependency_overrides[lambda: model_router] = lambda: new_router
        
        with TestClient(app) as client:
            yield client


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert data["service"] == "Aurea Orchestrator"


def test_select_model(client):
    """Test model selection endpoint."""
    response = client.get("/router/select")
    assert response.status_code == 200
    data = response.json()
    assert "selected_model" in data
    assert "score" in data
    assert "weights" in data


def test_record_metrics(client):
    """Test recording metrics."""
    payload = {
        "model": "gpt-4",
        "latency": 0.5,
        "cost": 0.02,
        "success": True
    }
    response = client.post("/router/record", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "recorded"
    assert data["model"] == "gpt-4"


def test_get_metrics(client):
    """Test getting metrics summary."""
    # First record some data
    payload = {
        "model": "gpt-3.5-turbo",
        "latency": 0.3,
        "cost": 0.002,
        "success": True
    }
    client.post("/router/record", json=payload)
    
    # Get metrics
    response = client.get("/router/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "gpt-3.5-turbo" in data
    assert data["gpt-3.5-turbo"]["total_requests"] >= 1


def test_optimize_weights(client):
    """Test weight optimization endpoint."""
    # Record some data first
    for i in range(5):
        client.post("/router/record", json={
            "model": "gpt-4",
            "latency": 0.8,
            "cost": 0.03,
            "success": True
        })
        client.post("/router/record", json={
            "model": "gpt-3.5-turbo",
            "latency": 0.3,
            "cost": 0.002,
            "success": True
        })
    
    response = client.post("/router/optimize")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "optimized"
    assert "weights" in data
    assert "metrics_summary" in data


def test_get_weights(client):
    """Test getting current weights."""
    response = client.get("/router/weights")
    assert response.status_code == 200
    data = response.json()
    assert "cost_weight" in data
    assert "quality_weight" in data
    assert "latency_weight" in data


def test_update_weights(client):
    """Test updating weights."""
    new_weights = {
        "cost_weight": 0.5,
        "quality_weight": 0.3,
        "latency_weight": 0.2
    }
    response = client.put("/router/weights", json=new_weights)
    assert response.status_code == 200
    data = response.json()
    assert abs(data["cost_weight"] - 0.5) < 0.01


def test_update_weights_invalid_sum(client):
    """Test that invalid weights are rejected."""
    invalid_weights = {
        "cost_weight": 0.5,
        "quality_weight": 0.5,
        "latency_weight": 0.5
    }
    response = client.put("/router/weights", json=invalid_weights)
    assert response.status_code == 400
