"""Tests for agents."""

import pytest
from unittest.mock import Mock, patch

from aurea_orchestrator.agents import (
    ContextAgent,
    ArchitectAgent,
    CodeAgent,
    TestAgent,
    ReviewAgent,
)
from aurea_orchestrator.schemas import AgentType, WorkflowState, TaskStatus


class TestContextAgent:
    """Test the ContextAgent class."""

    def test_agent_type(self):
        """Test that agent type is correct."""
        agent = ContextAgent()
        assert agent.agent_type == AgentType.CONTEXT

    def test_system_prompt(self):
        """Test that system prompt is defined."""
        agent = ContextAgent()
        prompt = agent.get_system_prompt()
        assert len(prompt) > 0
        assert "context" in prompt.lower() or "analysis" in prompt.lower()

    @patch("aurea_orchestrator.agents.model_router")
    def test_process(self, mock_router):
        """Test processing a workflow state."""
        # Setup mock
        mock_model = Mock()
        mock_model.invoke = Mock(return_value=Mock(content="Context analysis result"))
        mock_router.get_model.return_value = mock_model

        agent = ContextAgent()
        state = WorkflowState(
            task_id="test-123",
            task_description="Test task",
            status=TaskStatus.PENDING,
        )

        result = agent.process(state)

        assert "context" in result
        assert result["context"] == "Context analysis result"
        mock_router.get_model.assert_called_once()


class TestArchitectAgent:
    """Test the ArchitectAgent class."""

    def test_agent_type(self):
        """Test that agent type is correct."""
        agent = ArchitectAgent()
        assert agent.agent_type == AgentType.ARCHITECT

    def test_system_prompt(self):
        """Test that system prompt is defined."""
        agent = ArchitectAgent()
        prompt = agent.get_system_prompt()
        assert len(prompt) > 0
        assert "architect" in prompt.lower() or "design" in prompt.lower()

    @patch("aurea_orchestrator.agents.model_router")
    def test_process(self, mock_router):
        """Test processing a workflow state."""
        mock_model = Mock()
        mock_model.invoke = Mock(return_value=Mock(content="Architecture design"))
        mock_router.get_model.return_value = mock_model

        agent = ArchitectAgent()
        state = WorkflowState(
            task_id="test-123",
            task_description="Test task",
            status=TaskStatus.IN_PROGRESS,
            context="Test context",
        )

        result = agent.process(state)

        assert "architecture" in result
        assert result["architecture"] == "Architecture design"


class TestCodeAgent:
    """Test the CodeAgent class."""

    def test_agent_type(self):
        """Test that agent type is correct."""
        agent = CodeAgent()
        assert agent.agent_type == AgentType.CODE

    def test_system_prompt(self):
        """Test that system prompt is defined."""
        agent = CodeAgent()
        prompt = agent.get_system_prompt()
        assert len(prompt) > 0
        assert "code" in prompt.lower()

    @patch("aurea_orchestrator.agents.model_router")
    def test_process(self, mock_router):
        """Test processing a workflow state."""
        mock_model = Mock()
        mock_model.invoke = Mock(return_value=Mock(content="Generated code"))
        mock_router.get_model.return_value = mock_model

        agent = CodeAgent()
        state = WorkflowState(
            task_id="test-123",
            task_description="Test task",
            status=TaskStatus.IN_PROGRESS,
            context="Test context",
            architecture="Test architecture",
        )

        result = agent.process(state)

        assert "code" in result
        assert result["code"] == "Generated code"


class TestTestAgent:
    """Test the TestAgent class."""

    def test_agent_type(self):
        """Test that agent type is correct."""
        agent = TestAgent()
        assert agent.agent_type == AgentType.TEST

    def test_system_prompt(self):
        """Test that system prompt is defined."""
        agent = TestAgent()
        prompt = agent.get_system_prompt()
        assert len(prompt) > 0
        assert "test" in prompt.lower()

    @patch("aurea_orchestrator.agents.model_router")
    def test_process(self, mock_router):
        """Test processing a workflow state."""
        mock_model = Mock()
        mock_model.invoke = Mock(return_value=Mock(content="Generated tests"))
        mock_router.get_model.return_value = mock_model

        agent = TestAgent()
        state = WorkflowState(
            task_id="test-123",
            task_description="Test task",
            status=TaskStatus.IN_PROGRESS,
            code="Test code",
        )

        result = agent.process(state)

        assert "tests" in result
        assert result["tests"] == "Generated tests"


class TestReviewAgent:
    """Test the ReviewAgent class."""

    def test_agent_type(self):
        """Test that agent type is correct."""
        agent = ReviewAgent()
        assert agent.agent_type == AgentType.REVIEW

    def test_system_prompt(self):
        """Test that system prompt is defined."""
        agent = ReviewAgent()
        prompt = agent.get_system_prompt()
        assert len(prompt) > 0
        assert "review" in prompt.lower()

    @patch("aurea_orchestrator.agents.model_router")
    def test_process(self, mock_router):
        """Test processing a workflow state."""
        mock_model = Mock()
        mock_model.invoke = Mock(return_value=Mock(content="Code review"))
        mock_router.get_model.return_value = mock_model

        agent = ReviewAgent()
        state = WorkflowState(
            task_id="test-123",
            task_description="Test task",
            status=TaskStatus.IN_PROGRESS,
            code="Test code",
            tests="Test tests",
        )

        result = agent.process(state)

        assert "review" in result
        assert result["review"] == "Code review"
