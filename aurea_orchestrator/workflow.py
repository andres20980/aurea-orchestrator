"""Workflow orchestration using LangGraph."""

from typing import Any, Dict

from langgraph.graph import END, StateGraph

from aurea_orchestrator.agents import (
    ArchitectAgent,
    CodeAgent,
    ContextAgent,
    ReviewAgent,
    TestAgent,
)
from aurea_orchestrator.schemas import TaskStatus, WorkflowState


class WorkflowOrchestrator:
    """Orchestrates the multi-agent workflow using LangGraph."""

    def __init__(self):
        """Initialize the workflow orchestrator."""
        self.context_agent = ContextAgent()
        self.architect_agent = ArchitectAgent()
        self.code_agent = CodeAgent()
        self.test_agent = TestAgent()
        self.review_agent = ReviewAgent()

        # Build the workflow graph
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow.

        Returns:
            Compiled StateGraph workflow
        """
        # Create a new graph with WorkflowState schema
        workflow = StateGraph(WorkflowState)

        # Add nodes for each agent
        workflow.add_node("context", self._context_node)
        workflow.add_node("architect", self._architect_node)
        workflow.add_node("code", self._code_node)
        workflow.add_node("test", self._test_node)
        workflow.add_node("review", self._review_node)

        # Define the workflow edges
        workflow.set_entry_point("context")
        workflow.add_edge("context", "architect")
        workflow.add_edge("architect", "code")
        workflow.add_edge("code", "test")
        workflow.add_edge("test", "review")
        workflow.add_edge("review", END)

        return workflow.compile()

    def _context_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Execute the context agent.

        Args:
            state: Current workflow state

        Returns:
            Updated state fields
        """
        updates = self.context_agent.process(state)
        updates["status"] = TaskStatus.IN_PROGRESS
        return updates

    def _architect_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Execute the architect agent.

        Args:
            state: Current workflow state

        Returns:
            Updated state fields
        """
        return self.architect_agent.process(state)

    def _code_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Execute the code agent.

        Args:
            state: Current workflow state

        Returns:
            Updated state fields
        """
        return self.code_agent.process(state)

    def _test_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Execute the test agent.

        Args:
            state: Current workflow state

        Returns:
            Updated state fields
        """
        return self.test_agent.process(state)

    def _review_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Execute the review agent.

        Args:
            state: Current workflow state

        Returns:
            Updated state fields
        """
        updates = self.review_agent.process(state)
        updates["status"] = TaskStatus.COMPLETED
        return updates

    def execute(self, state: WorkflowState) -> WorkflowState:
        """Execute the workflow.

        Args:
            state: Initial workflow state

        Returns:
            Final workflow state after execution
        """
        result = self.workflow.invoke(state.model_dump())
        return WorkflowState(**result)


# Global orchestrator instance
orchestrator = WorkflowOrchestrator()
