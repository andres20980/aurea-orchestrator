"""Tests for API endpoints"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from aurea_orchestrator.main import app
from aurea_orchestrator.models.database import Base
from aurea_orchestrator.models.config import get_db


# Create test database with proper settings for in-memory SQLite
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override the dependency
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True, scope="function")
def setup_database():
    """Setup test database before each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


class TestPromptAPI:
    """Test prompt template API endpoints"""
    
    def test_create_prompt_template(self):
        """Test creating a prompt template via API"""
        response = client.post(
            "/prompts/",
            json={
                "name": "greeting",
                "description": "A greeting template",
                "template_yaml": "prompt: Hello {{ name }}!",
                "variables": ["name"]
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "greeting"
        assert data["version"] == 1
        assert data["description"] == "A greeting template"
        assert data["variables"] == ["name"]
    
    def test_create_prompt_template_invalid_yaml(self):
        """Test creating template with invalid YAML"""
        response = client.post(
            "/prompts/",
            json={
                "name": "invalid",
                "template_yaml": "invalid: yaml: [unclosed"
            }
        )
        
        assert response.status_code == 422  # Pydantic validation error
    
    def test_list_prompt_templates(self):
        """Test listing prompt templates"""
        # Create some templates
        client.post(
            "/prompts/",
            json={"name": "template1", "template_yaml": "test1"}
        )
        client.post(
            "/prompts/",
            json={"name": "template2", "template_yaml": "test2"}
        )
        
        response = client.get("/prompts/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
    
    def test_get_prompt_template(self):
        """Test getting a specific prompt template"""
        # Create a template
        create_response = client.post(
            "/prompts/",
            json={"name": "test", "template_yaml": "content"}
        )
        template_id = create_response.json()["id"]
        
        # Get the template
        response = client.get(f"/prompts/{template_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == template_id
        assert data["name"] == "test"
    
    def test_get_prompt_template_not_found(self):
        """Test getting a non-existent template"""
        response = client.get("/prompts/9999")
        assert response.status_code == 404
    
    def test_get_prompt_template_by_name(self):
        """Test getting template by name"""
        client.post(
            "/prompts/",
            json={"name": "mytemplate", "template_yaml": "v1"}
        )
        client.post(
            "/prompts/",
            json={"name": "mytemplate", "template_yaml": "v2"}
        )
        
        # Get latest version
        response = client.get("/prompts/by-name/mytemplate")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "mytemplate"
        assert data["version"] == 2
        
        # Get specific version
        response = client.get("/prompts/by-name/mytemplate?version=1")
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == 1
    
    def test_update_prompt_template(self):
        """Test updating a prompt template"""
        # Create a template
        create_response = client.post(
            "/prompts/",
            json={"name": "test", "template_yaml": "original", "description": "Original"}
        )
        template_id = create_response.json()["id"]
        
        # Update the template
        response = client.put(
            f"/prompts/{template_id}",
            json={"description": "Updated", "template_yaml": "updated"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated"
        assert data["template_yaml"] == "updated"
    
    def test_delete_prompt_template(self):
        """Test deleting a prompt template"""
        # Create a template
        create_response = client.post(
            "/prompts/",
            json={"name": "test", "template_yaml": "content"}
        )
        template_id = create_response.json()["id"]
        
        # Delete the template
        response = client.delete(f"/prompts/{template_id}")
        assert response.status_code == 204
        
        # Template should still exist but be inactive
        get_response = client.get(f"/prompts/{template_id}")
        assert get_response.status_code == 200
    
    def test_preview_prompt_template(self):
        """Test previewing a prompt template"""
        response = client.post(
            "/prompts/preview",
            json={
                "template_yaml": "Hello {{ name }}!",
                "variables": {"name": "World"}
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["rendered"] == "Hello World!"
        assert data["variables_used"] == {"name": "World"}
    
    def test_preview_prompt_template_missing_variable(self):
        """Test previewing template with missing variable"""
        response = client.post(
            "/prompts/preview",
            json={
                "template_yaml": "Hello {{ name }}!",
                "variables": {}
            }
        )
        
        assert response.status_code == 400


class TestJobAPI:
    """Test job API endpoints"""
    
    def test_create_job_without_template(self):
        """Test creating a job without a template"""
        response = client.post(
            "/jobs/",
            json={
                "name": "test_job",
                "input_data": {"key": "value"}
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "test_job"
        assert data["status"] == "pending"
        assert data["input_data"] == {"key": "value"}
        assert data["prompt_template_id"] is None
    
    def test_create_job_with_template(self):
        """Test creating a job with a template"""
        # Create a template first
        template_response = client.post(
            "/prompts/",
            json={"name": "test_template", "template_yaml": "prompt: Hello!"}
        )
        template_id = template_response.json()["id"]
        
        # Create job with template
        response = client.post(
            "/jobs/",
            json={
                "name": "test_job",
                "prompt_template_id": template_id,
                "input_data": {"key": "value"}
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "test_job"
        assert data["prompt_template_id"] == template_id
        assert data["prompt_version"] == 1
    
    def test_list_jobs(self):
        """Test listing jobs"""
        client.post("/jobs/", json={"name": "job1"})
        client.post("/jobs/", json={"name": "job2"})
        
        response = client.get("/jobs/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
    
    def test_get_job(self):
        """Test getting a specific job"""
        # Create a job
        create_response = client.post(
            "/jobs/",
            json={"name": "test_job"}
        )
        job_id = create_response.json()["id"]
        
        # Get the job
        response = client.get(f"/jobs/{job_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == job_id
        assert data["name"] == "test_job"
    
    def test_get_job_with_prompt_version(self):
        """Test that job exposes which prompt version was used"""
        # Create template
        template_response = client.post(
            "/prompts/",
            json={"name": "test_template", "template_yaml": "v1"}
        )
        template_id = template_response.json()["id"]
        
        # Create another version
        client.post(
            "/prompts/",
            json={"name": "test_template", "template_yaml": "v2"}
        )
        
        # Create job with first version
        job_response = client.post(
            "/jobs/",
            json={"name": "test_job", "prompt_template_id": template_id}
        )
        job_id = job_response.json()["id"]
        
        # Get job and verify prompt version is exposed
        response = client.get(f"/jobs/{job_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["prompt_version"] == 1
        assert data["prompt_template_id"] == template_id


class TestRootEndpoints:
    """Test root endpoints"""
    
    def test_root(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
