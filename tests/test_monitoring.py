"""
Tests for the monitoring middleware and models.
"""
import pytest
import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Metric, get_job_stats
from middleware import monitor_task, estimate_default_cost, log_metric
import models
import middleware

# Use in-memory SQLite for testing
TEST_DATABASE_URL = 'sqlite:///:memory:'


@pytest.fixture(scope='function')
def test_db():
    """Create a test database."""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    
    # Monkey patch both modules to use test database
    original_get_engine = models.get_engine
    original_mw_get_session = middleware.get_session
    
    def test_get_engine():
        return engine
    
    def test_get_session():
        Session = sessionmaker(bind=engine)
        return Session()
    
    models.get_engine = test_get_engine
    models.get_session = test_get_session
    middleware.get_session = test_get_session
    
    yield engine
    
    # Cleanup
    models.get_engine = original_get_engine
    models.get_session = original_mw_get_session
    middleware.get_session = original_mw_get_session
    Base.metadata.drop_all(engine)


def test_metric_creation(test_db):
    """Test creating and storing a metric."""
    log_metric(
        job_id='test_job_1',
        task_name='test_task',
        model_used='gpt-4',
        token_count=100,
        latency_ms=500.5,
        cost_estimate=0.003
    )
    
    # Verify the metric was created
    from models import get_session
    session = get_session()
    metric = session.query(Metric).filter(Metric.job_id == 'test_job_1').first()
    
    assert metric is not None
    assert metric.task_name == 'test_task'
    assert metric.model_used == 'gpt-4'
    assert metric.token_count == 100
    assert metric.latency_ms == 500.5
    assert metric.cost_estimate == 0.003
    
    session.close()


def test_get_job_stats(test_db):
    """Test aggregated statistics calculation."""
    # Create multiple metrics for the same job
    log_metric('job_1', 'task_a', 'gpt-4', 100, 500, 0.003)
    log_metric('job_1', 'task_a', 'gpt-4', 150, 600, 0.0045)
    log_metric('job_1', 'task_b', 'claude-3-sonnet', 200, 700, 0.0006)
    
    stats = get_job_stats('job_1')
    
    assert stats['job_id'] == 'job_1'
    assert stats['total_tasks'] == 3
    assert stats['total_tokens'] == 450
    assert stats['total_cost'] == pytest.approx(0.0081, rel=1e-4)
    assert stats['avg_latency_ms'] == pytest.approx(600.0, rel=1e-4)
    
    # Check task breakdown
    assert len(stats['task_breakdown']) == 2
    task_a = next(t for t in stats['task_breakdown'] if t['task_name'] == 'task_a')
    assert task_a['count'] == 2
    
    # Check model usage
    assert len(stats['model_usage']) == 2
    gpt4 = next(m for m in stats['model_usage'] if m['model'] == 'gpt-4')
    assert gpt4['total_tokens'] == 250


def test_monitor_task_decorator(test_db):
    """Test the monitoring decorator."""
    @monitor_task('job_2', 'test_function', 'gpt-3.5-turbo')
    def test_function():
        time.sleep(0.1)  # Simulate work
        return "result", 50  # Return result and token count
    
    result = test_function()
    
    # Check that metric was logged
    stats = get_job_stats('job_2')
    assert stats['total_tasks'] == 1
    assert stats['total_tokens'] == 50
    assert stats['avg_latency_ms'] >= 100  # At least 100ms due to sleep


def test_monitor_task_with_dict_result(test_db):
    """Test monitoring when function returns a dict."""
    @monitor_task('job_3', 'dict_task', 'claude-3-opus')
    def dict_task():
        return {'result': 'data', 'tokens': 75}
    
    result = dict_task()
    
    stats = get_job_stats('job_3')
    assert stats['total_tasks'] == 1
    assert stats['total_tokens'] == 75


def test_cost_estimation():
    """Test cost estimation function."""
    # Test known models
    gpt4_cost = estimate_default_cost('gpt-4', 1000)
    assert gpt4_cost == 0.03
    
    claude_cost = estimate_default_cost('claude-3-sonnet', 1000)
    assert claude_cost == 0.003
    
    # Test unknown model (should use default)
    unknown_cost = estimate_default_cost('unknown-model', 1000)
    assert unknown_cost == 0.001


def test_multiple_jobs(test_db):
    """Test handling multiple jobs."""
    log_metric('job_a', 'task_1', 'gpt-4', 100, 500, 0.003)
    log_metric('job_b', 'task_1', 'gpt-4', 200, 600, 0.006)
    
    stats_a = get_job_stats('job_a')
    stats_b = get_job_stats('job_b')
    
    assert stats_a['total_tasks'] == 1
    assert stats_b['total_tasks'] == 1
    assert stats_a['total_tokens'] == 100
    assert stats_b['total_tokens'] == 200


def test_metric_to_dict():
    """Test metric to dict conversion."""
    metric = Metric(
        id=1,
        job_id='test_job',
        task_name='test_task',
        model_used='gpt-4',
        token_count=100,
        latency_ms=500.5,
        cost_estimate=0.003
    )
    
    metric_dict = metric.to_dict()
    
    assert metric_dict['id'] == 1
    assert metric_dict['job_id'] == 'test_job'
    assert metric_dict['task_name'] == 'test_task'
    assert metric_dict['token_count'] == 100


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
