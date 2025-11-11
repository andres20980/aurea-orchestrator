"""
Tests for the Aurea Orchestrator benchmark API
"""
import json
import pytest
import time
from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    """Test the health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['service'] == 'aurea-orchestrator'


def test_benchmark_run_basic(client):
    """Test basic benchmark run with minimal jobs"""
    payload = {
        'num_jobs': 5,
        'job_duration_ms': 50
    }
    
    response = client.post('/benchmark/run', 
                          data=json.dumps(payload),
                          content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Verify response structure
    assert 'benchmark_id' in data
    assert data['num_jobs'] == 5
    assert data['completed_jobs'] == 5
    assert 'throughput' in data
    assert 'mean_latency' in data
    assert 'total_cost' in data
    assert 'start_time' in data
    assert 'end_time' in data
    assert 'duration' in data
    assert 'jobs' in data
    
    # Verify metrics are positive
    assert data['throughput'] > 0
    assert data['mean_latency'] > 0
    assert data['total_cost'] >= 0
    assert len(data['jobs']) == 5


def test_benchmark_run_with_multiple_jobs(client):
    """Test benchmark with more jobs"""
    payload = {
        'num_jobs': 20,
        'job_duration_ms': 100
    }
    
    response = client.post('/benchmark/run',
                          data=json.dumps(payload),
                          content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['completed_jobs'] == 20


def test_benchmark_run_missing_num_jobs(client):
    """Test benchmark with missing num_jobs parameter"""
    payload = {}
    
    response = client.post('/benchmark/run',
                          data=json.dumps(payload),
                          content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data


def test_benchmark_run_invalid_num_jobs(client):
    """Test benchmark with invalid num_jobs values"""
    # Test with negative number
    payload = {'num_jobs': -5}
    response = client.post('/benchmark/run',
                          data=json.dumps(payload),
                          content_type='application/json')
    assert response.status_code == 400
    
    # Test with zero
    payload = {'num_jobs': 0}
    response = client.post('/benchmark/run',
                          data=json.dumps(payload),
                          content_type='application/json')
    assert response.status_code == 400
    
    # Test with non-integer
    payload = {'num_jobs': 'invalid'}
    response = client.post('/benchmark/run',
                          data=json.dumps(payload),
                          content_type='application/json')
    assert response.status_code == 400


def test_benchmark_run_invalid_job_duration(client):
    """Test benchmark with invalid job_duration_ms"""
    payload = {
        'num_jobs': 5,
        'job_duration_ms': -100
    }
    
    response = client.post('/benchmark/run',
                          data=json.dumps(payload),
                          content_type='application/json')
    
    assert response.status_code == 400


def test_benchmark_run_default_duration(client):
    """Test benchmark with default job duration"""
    payload = {
        'num_jobs': 3
    }
    
    response = client.post('/benchmark/run',
                          data=json.dumps(payload),
                          content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['completed_jobs'] == 3


def test_metrics_endpoint(client):
    """Test the Prometheus metrics endpoint"""
    response = client.get('/metrics')
    assert response.status_code == 200
    assert b'benchmark_runs_total' in response.data
    assert b'benchmark_jobs_total' in response.data
    assert b'benchmark_throughput_jobs_per_second' in response.data
    assert b'benchmark_mean_latency_seconds' in response.data
    assert b'benchmark_cost_total' in response.data


def test_benchmark_run_invalid_json(client):
    """Test benchmark with invalid JSON"""
    response = client.post('/benchmark/run',
                          data='not json',
                          content_type='application/json')
    
    assert response.status_code == 400
