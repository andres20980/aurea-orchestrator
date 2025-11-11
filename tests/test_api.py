"""
Tests for the Flask API endpoints.
"""
import pytest
import json
from app import create_app
from models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models
import middleware

TEST_DATABASE_URL = 'sqlite:///:memory:'


@pytest.fixture(scope='function')
def app():
    """Create and configure a test app instance."""
    # Set up test database
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    
    # Monkey patch to use test database
    original_get_engine = models.get_engine
    original_models_get_session = models.get_session
    original_mw_get_session = middleware.get_session
    
    def test_get_engine():
        return engine
    
    def test_get_session():
        Session = sessionmaker(bind=engine)
        return Session()
    
    models.get_engine = test_get_engine
    models.get_session = test_get_session
    middleware.get_session = test_get_session
    
    # Create app
    app = create_app()
    app.config['TESTING'] = True
    
    yield app
    
    # Cleanup
    models.get_engine = original_get_engine
    models.get_session = original_models_get_session
    middleware.get_session = original_mw_get_session
    Base.metadata.drop_all(engine)


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'


def test_create_metric(client):
    """Test creating a metric via API."""
    metric_data = {
        'job_id': 'test_job_1',
        'task_name': 'test_task',
        'model_used': 'gpt-4',
        'token_count': 100,
        'latency_ms': 500.5,
        'cost_estimate': 0.003
    }
    
    response = client.post(
        '/metrics',
        data=json.dumps(metric_data),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'message' in data


def test_create_metric_missing_fields(client):
    """Test creating metric with missing fields."""
    metric_data = {
        'job_id': 'test_job_1',
        'task_name': 'test_task'
        # Missing required fields
    }
    
    response = client.post(
        '/metrics',
        data=json.dumps(metric_data),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data


def test_get_job_metrics(client):
    """Test getting job metrics."""
    # First create some metrics
    metrics = [
        {
            'job_id': 'job_123',
            'task_name': 'task_a',
            'model_used': 'gpt-4',
            'token_count': 100,
            'latency_ms': 500.0,
            'cost_estimate': 0.003
        },
        {
            'job_id': 'job_123',
            'task_name': 'task_b',
            'model_used': 'claude-3-sonnet',
            'token_count': 200,
            'latency_ms': 600.0,
            'cost_estimate': 0.006
        }
    ]
    
    for metric in metrics:
        client.post('/metrics', data=json.dumps(metric), content_type='application/json')
    
    # Get aggregated stats
    response = client.get('/metrics/jobs/job_123')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['job_id'] == 'job_123'
    assert data['total_tasks'] == 2
    assert data['total_tokens'] == 300
    assert len(data['task_breakdown']) == 2


def test_get_job_details(client):
    """Test getting detailed job metrics."""
    # Create a metric
    metric_data = {
        'job_id': 'job_456',
        'task_name': 'test_task',
        'model_used': 'gpt-4',
        'token_count': 150,
        'latency_ms': 750.0,
        'cost_estimate': 0.0045
    }
    
    client.post('/metrics', data=json.dumps(metric_data), content_type='application/json')
    
    # Get details
    response = client.get('/metrics/jobs/job_456/details')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['job_id'] == 'job_456'
    assert data['count'] == 1
    assert len(data['metrics']) == 1
    assert data['metrics'][0]['task_name'] == 'test_task'


def test_list_jobs(client):
    """Test listing all jobs."""
    # Create metrics for different jobs
    jobs = ['job_a', 'job_b', 'job_c']
    for job_id in jobs:
        metric_data = {
            'job_id': job_id,
            'task_name': 'test_task',
            'model_used': 'gpt-4',
            'token_count': 100,
            'latency_ms': 500.0,
            'cost_estimate': 0.003
        }
        client.post('/metrics', data=json.dumps(metric_data), content_type='application/json')
    
    # List all jobs
    response = client.get('/metrics/jobs')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'jobs' in data
    assert len(data['jobs']) == 3
    job_ids = [j['job_id'] for j in data['jobs']]
    for job_id in jobs:
        assert job_id in job_ids


def test_pagination(client):
    """Test pagination for job details."""
    # Create multiple metrics
    for i in range(5):
        metric_data = {
            'job_id': 'job_pagination',
            'task_name': f'task_{i}',
            'model_used': 'gpt-4',
            'token_count': 100,
            'latency_ms': 500.0,
            'cost_estimate': 0.003
        }
        client.post('/metrics', data=json.dumps(metric_data), content_type='application/json')
    
    # Get first page
    response = client.get('/metrics/jobs/job_pagination/details?limit=2&offset=0')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['count'] == 2
    
    # Get second page
    response = client.get('/metrics/jobs/job_pagination/details?limit=2&offset=2')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['count'] == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
