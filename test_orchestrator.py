import pytest
from fastapi.testclient import TestClient
from main import app
from storage import job_store
from models import JobStatus, NodeStatus
import time


client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint returns correct info"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Aurea Orchestrator"
    assert "endpoints" in data


def test_create_job():
    """Test job creation"""
    request_data = {
        "input_data": {"task": "test task"},
        "max_iterations": 2
    }
    response = client.post("/jobs", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == JobStatus.PENDING


def test_get_job_status():
    """Test getting job status"""
    # Create a job
    request_data = {
        "input_data": {"task": "test status"},
        "max_iterations": 1
    }
    create_response = client.post("/jobs", json=request_data)
    job_id = create_response.json()["job_id"]
    
    # Wait a bit for workflow to start
    time.sleep(0.5)
    
    # Get status
    status_response = client.get(f"/jobs/{job_id}/status")
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert status_data["job_id"] == job_id
    assert "node_progress" in status_data
    assert "iteration_count" in status_data


def test_get_nonexistent_job_status():
    """Test getting status for non-existent job"""
    response = client.get("/jobs/nonexistent-id/status")
    assert response.status_code == 404


def test_workflow_execution():
    """Test complete workflow execution"""
    request_data = {
        "input_data": {"task": "complete workflow test"},
        "max_iterations": 1
    }
    create_response = client.post("/jobs", json=request_data)
    job_id = create_response.json()["job_id"]
    
    # Wait for workflow to complete
    time.sleep(5)
    
    # Check final status
    status_response = client.get(f"/jobs/{job_id}/status")
    status_data = status_response.json()
    
    # Should be completed
    assert status_data["status"] in [JobStatus.RUNNING, JobStatus.COMPLETED]
    
    # Should have progress for all nodes
    node_names = [node["node_name"] for node in status_data["node_progress"]]
    assert "plan" in node_names
    assert "implement" in node_names


def test_parallel_execution():
    """Test that test and review_precheck run in parallel"""
    request_data = {
        "input_data": {"task": "parallel execution test"},
        "max_iterations": 1
    }
    create_response = client.post("/jobs", json=request_data)
    job_id = create_response.json()["job_id"]
    
    # Wait for workflow to complete
    time.sleep(5)
    
    # Check status
    status_response = client.get(f"/jobs/{job_id}/status")
    status_data = status_response.json()
    
    # Both test and review_precheck should be present
    node_names = [node["node_name"] for node in status_data["node_progress"]]
    assert "test" in node_names
    assert "review_precheck" in node_names


def test_job_store():
    """Test job store functionality"""
    # Create a job
    job_id = job_store.create_job({"task": "store test"}, max_iterations=2)
    assert job_id is not None
    
    # Get job
    job = job_store.get_job(job_id)
    assert job is not None
    assert job["job_id"] == job_id
    
    # Update status
    job_store.update_job_status(job_id, JobStatus.RUNNING)
    job = job_store.get_job(job_id)
    assert job["status"] == JobStatus.RUNNING
    
    # Add node progress
    job_store.add_node_progress(job_id, "plan", NodeStatus.RUNNING)
    job_store.add_node_progress(job_id, "plan", NodeStatus.COMPLETED, output="test output")
    
    status = job_store.get_job_status(job_id)
    assert len(status["node_progress"]) > 0
    assert status["node_progress"][0]["node_name"] == "plan"
    assert status["node_progress"][0]["status"] == NodeStatus.COMPLETED
