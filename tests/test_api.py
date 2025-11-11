"""Integration tests for the API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from src.sandbox.api import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert data["name"] == "Aurea Sandbox Orchestrator"


def test_health_endpoint_success(client):
    """Test health endpoint when Docker is available."""
    with patch("docker.from_env") as mock_docker:
        mock_client = MagicMock()
        mock_client.version.return_value = {"Version": "20.10.0"}
        mock_docker.return_value = mock_client
        
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["sandbox_available"] is True
        assert data["docker_version"] == "20.10.0"


def test_health_endpoint_docker_unavailable(client):
    """Test health endpoint when Docker is unavailable."""
    with patch("docker.from_env") as mock_docker:
        mock_docker.side_effect = Exception("Docker not available")
        
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["sandbox_available"] is False


def test_submit_run_validation(client):
    """Test run submission with validation."""
    # Test with invalid timeout
    response = client.post("/run", json={
        "code": "print('hello')",
        "language": "python",
        "timeout": 400  # Exceeds maximum
    })
    assert response.status_code == 422  # Validation error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
