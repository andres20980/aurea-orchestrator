"""Tests for FastAPI endpoints."""

from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from aurea_orchestrator.main import app
from aurea_orchestrator.schemas import TaskStatus


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


class TestAPIEndpoints:
    """Test API endpoints."""

    def test_root_endpoint(self, client):
        """Test the root endpoint."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert data["name"] == "Aurea Orchestrator"

    def test_health_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    @patch("aurea_orchestrator.main.process_task")
    def test_create_task(self, mock_process_task, client):
        """Test creating a new task."""
        mock_process_task.delay = Mock()

        response = client.post(
            "/tasks",
            json={
                "description": "Test task",
                "metadata": {"test": True},
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert data["status"] == TaskStatus.PENDING.value
        mock_process_task.delay.assert_called_once()

    @patch("aurea_orchestrator.main.celery_app")
    def test_get_task_pending(self, mock_celery_app, client):
        """Test getting a pending task."""
        mock_result = Mock()
        mock_result.state = "PENDING"
        mock_celery_app.AsyncResult.return_value = mock_result

        response = client.get("/tasks/test-task-id")

        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "test-task-id"
        assert data["status"] == TaskStatus.PENDING.value

    @patch("aurea_orchestrator.main.celery_app")
    def test_get_task_success(self, mock_celery_app, client):
        """Test getting a completed task."""
        mock_result = Mock()
        mock_result.state = "SUCCESS"
        mock_result.result = {"context": "Test context"}
        mock_celery_app.AsyncResult.return_value = mock_result

        response = client.get("/tasks/test-task-id")

        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "test-task-id"
        assert data["status"] == TaskStatus.COMPLETED.value
        assert data["result"] is not None

    @patch("aurea_orchestrator.main.celery_app")
    def test_get_task_result(self, mock_celery_app, client):
        """Test getting task results."""
        mock_result = Mock()
        mock_result.ready.return_value = True
        mock_result.failed.return_value = False
        mock_result.result = {
            "context": "Test context",
            "architecture": "Test architecture",
        }
        mock_celery_app.AsyncResult.return_value = mock_result

        response = client.get("/tasks/test-task-id/result")

        assert response.status_code == 200
        data = response.json()
        assert "context" in data
        assert "architecture" in data

    @patch("aurea_orchestrator.main.celery_app")
    def test_get_task_result_not_ready(self, mock_celery_app, client):
        """Test getting task results when not ready."""
        mock_result = Mock()
        mock_result.ready.return_value = False
        mock_celery_app.AsyncResult.return_value = mock_result

        response = client.get("/tasks/test-task-id/result")

        assert response.status_code == 404
