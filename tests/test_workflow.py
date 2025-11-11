"""Tests for workflow orchestration."""

import pytest
from unittest.mock import Mock, patch

from aurea_orchestrator.schemas import WorkflowState, TaskStatus
from aurea_orchestrator.workflow import WorkflowOrchestrator


class TestWorkflowOrchestrator:
    """Test the WorkflowOrchestrator class."""

    def test_initialization(self):
        """Test that orchestrator initializes correctly."""
        orchestrator = WorkflowOrchestrator()

        assert orchestrator.context_agent is not None
        assert orchestrator.architect_agent is not None
        assert orchestrator.code_agent is not None
        assert orchestrator.test_agent is not None
        assert orchestrator.review_agent is not None
        assert orchestrator.workflow is not None

    @patch("aurea_orchestrator.workflow.ContextAgent")
    @patch("aurea_orchestrator.workflow.ArchitectAgent")
    @patch("aurea_orchestrator.workflow.CodeAgent")
    @patch("aurea_orchestrator.workflow.TestAgent")
    @patch("aurea_orchestrator.workflow.ReviewAgent")
    def test_context_node(
        self, mock_review, mock_test, mock_code, mock_architect, mock_context
    ):
        """Test the context node execution."""
        mock_agent = Mock()
        mock_agent.process.return_value = {"context": "Test context"}
        mock_context.return_value = mock_agent

        orchestrator = WorkflowOrchestrator()
        state = WorkflowState(
            task_id="test-123",
            task_description="Test task",
            status=TaskStatus.PENDING,
        )

        result = orchestrator._context_node(state)

        assert result["context"] == "Test context"
        assert result["status"] == TaskStatus.IN_PROGRESS

    @patch("aurea_orchestrator.workflow.ContextAgent")
    @patch("aurea_orchestrator.workflow.ArchitectAgent")
    @patch("aurea_orchestrator.workflow.CodeAgent")
    @patch("aurea_orchestrator.workflow.TestAgent")
    @patch("aurea_orchestrator.workflow.ReviewAgent")
    def test_review_node_sets_completed_status(
        self, mock_review, mock_test, mock_code, mock_architect, mock_context
    ):
        """Test that review node sets status to completed."""
        mock_agent = Mock()
        mock_agent.process.return_value = {"review": "Test review"}
        mock_review.return_value = mock_agent

        orchestrator = WorkflowOrchestrator()
        state = WorkflowState(
            task_id="test-123",
            task_description="Test task",
            status=TaskStatus.IN_PROGRESS,
        )

        result = orchestrator._review_node(state)

        assert result["review"] == "Test review"
        assert result["status"] == TaskStatus.COMPLETED
