"""Test configuration and fixtures."""

from unittest.mock import Mock

import pytest

from aurea_orchestrator.config import Settings


@pytest.fixture
def mock_settings():
    """Provide mock settings for testing."""
    return Settings(
        anthropic_api_key="test-anthropic-key",
        openai_api_key="test-openai-key",
        database_url="postgresql://test:test@localhost:5432/test",
        redis_url="redis://localhost:6379/0",
        celery_broker_url="redis://localhost:6379/0",
        celery_result_backend="redis://localhost:6379/1",
        claude_model="claude-3-sonnet-20240229",
        deepseek_model="gpt-3.5-turbo",
        complexity_threshold=0.5,
    )


@pytest.fixture
def mock_llm():
    """Provide a mock language model."""
    mock = Mock()
    mock.invoke = Mock(return_value=Mock(content="Test response"))
    return mock
