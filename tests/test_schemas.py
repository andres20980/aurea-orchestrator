"""Tests for schemas."""

from aurea_orchestrator.schemas import (
    AgentMessage,
    AgentType,
    TaskRequest,
    TaskResponse,
    TaskStatus,
    WorkflowState,
)


class TestSchemas:
    """Test schema definitions."""

    def test_agent_type_enum(self):
        """Test AgentType enum."""
        assert AgentType.CONTEXT == "context"
        assert AgentType.ARCHITECT == "architect"
        assert AgentType.CODE == "code"
        assert AgentType.TEST == "test"
        assert AgentType.REVIEW == "review"

    def test_task_status_enum(self):
        """Test TaskStatus enum."""
        assert TaskStatus.PENDING == "pending"
        assert TaskStatus.IN_PROGRESS == "in_progress"
        assert TaskStatus.COMPLETED == "completed"
        assert TaskStatus.FAILED == "failed"

    def test_agent_message(self):
        """Test AgentMessage schema."""
        message = AgentMessage(
            agent_type=AgentType.CONTEXT,
            content="Test content",
            metadata={"key": "value"},
        )

        assert message.agent_type == AgentType.CONTEXT
        assert message.content == "Test content"
        assert message.metadata["key"] == "value"

    def test_workflow_state(self):
        """Test WorkflowState schema."""
        state = WorkflowState(
            task_id="test-123",
            task_description="Test task",
            status=TaskStatus.PENDING,
        )

        assert state.task_id == "test-123"
        assert state.task_description == "Test task"
        assert state.status == TaskStatus.PENDING
        assert state.context is None
        assert state.messages == []

    def test_workflow_state_with_results(self):
        """Test WorkflowState with results."""
        state = WorkflowState(
            task_id="test-123",
            task_description="Test task",
            status=TaskStatus.COMPLETED,
            context="Test context",
            architecture="Test architecture",
            code="Test code",
            tests="Test tests",
            review="Test review",
        )

        assert state.context == "Test context"
        assert state.architecture == "Test architecture"
        assert state.code == "Test code"
        assert state.tests == "Test tests"
        assert state.review == "Test review"

    def test_task_request(self):
        """Test TaskRequest schema."""
        request = TaskRequest(
            description="Test task",
            metadata={"key": "value"},
        )

        assert request.description == "Test task"
        assert request.metadata["key"] == "value"

    def test_task_response(self):
        """Test TaskResponse schema."""
        response = TaskResponse(
            task_id="test-123",
            status=TaskStatus.COMPLETED,
            result={"context": "Test context"},
        )

        assert response.task_id == "test-123"
        assert response.status == TaskStatus.COMPLETED
        assert response.result["context"] == "Test context"
