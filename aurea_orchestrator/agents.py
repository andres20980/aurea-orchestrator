"""Base agent class and specific agent implementations."""

from abc import ABC, abstractmethod
from typing import Dict, Any

from langchain.schema import BaseLanguageModel, HumanMessage, SystemMessage

from aurea_orchestrator.model_router import model_router
from aurea_orchestrator.schemas import AgentType, WorkflowState


class BaseAgent(ABC):
    """Base class for all agents."""

    def __init__(self, agent_type: AgentType):
        """Initialize the agent.

        Args:
            agent_type: Type of the agent
        """
        self.agent_type = agent_type

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        pass

    def process(self, state: WorkflowState) -> Dict[str, Any]:
        """Process the workflow state.

        Args:
            state: Current workflow state

        Returns:
            Dictionary with updates to apply to state
        """
        # Get appropriate model based on task complexity
        model = model_router.get_model(state.task_description, state.metadata)

        # Prepare messages
        system_prompt = self.get_system_prompt()
        user_message = self._prepare_user_message(state)

        # Get response from model
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message),
        ]

        response = model.invoke(messages)

        # Process the response
        return self._process_response(response.content, state)

    @abstractmethod
    def _prepare_user_message(self, state: WorkflowState) -> str:
        """Prepare the user message for the model."""
        pass

    @abstractmethod
    def _process_response(self, response: str, state: WorkflowState) -> Dict[str, Any]:
        """Process the model response and return state updates."""
        pass


class ContextAgent(BaseAgent):
    """Agent responsible for understanding and analyzing the task context."""

    def __init__(self):
        super().__init__(AgentType.CONTEXT)

    def get_system_prompt(self) -> str:
        return """You are a Context Analysis Agent. Your role is to:
1. Analyze the task description thoroughly
2. Identify key requirements and constraints
3. Determine the scope and complexity
4. Extract important technical details
5. Provide a comprehensive context summary

Be thorough and precise in your analysis."""

    def _prepare_user_message(self, state: WorkflowState) -> str:
        return f"""Analyze the following task and provide a comprehensive context:

Task Description: {state.task_description}

Provide:
1. Key requirements
2. Technical constraints
3. Scope analysis
4. Complexity assessment
5. Important considerations"""

    def _process_response(self, response: str, state: WorkflowState) -> Dict[str, Any]:
        return {"context": response}


class ArchitectAgent(BaseAgent):
    """Agent responsible for designing the architecture."""

    def __init__(self):
        super().__init__(AgentType.ARCHITECT)

    def get_system_prompt(self) -> str:
        return """You are an Architecture Design Agent. Your role is to:
1. Design a robust software architecture
2. Define system components and their interactions
3. Specify design patterns and best practices
4. Consider scalability and maintainability
5. Create a clear architectural plan

Focus on clean, scalable, and maintainable designs."""

    def _prepare_user_message(self, state: WorkflowState) -> str:
        context_info = f"\n\nContext Analysis:\n{state.context}" if state.context else ""

        return f"""Design the architecture for the following task:

Task Description: {state.task_description}{context_info}

Provide:
1. System architecture overview
2. Component breakdown
3. Design patterns to use
4. Data flow
5. Technology stack recommendations"""

    def _process_response(self, response: str, state: WorkflowState) -> Dict[str, Any]:
        return {"architecture": response}


class CodeAgent(BaseAgent):
    """Agent responsible for generating code."""

    def __init__(self):
        super().__init__(AgentType.CODE)

    def get_system_prompt(self) -> str:
        return """You are a Code Generation Agent. Your role is to:
1. Write clean, efficient, and well-documented code
2. Follow best practices and coding standards
3. Implement the designed architecture
4. Handle edge cases and errors
5. Write maintainable and testable code

Focus on code quality and best practices."""

    def _prepare_user_message(self, state: WorkflowState) -> str:
        context_info = f"\n\nContext:\n{state.context}" if state.context else ""
        arch_info = f"\n\nArchitecture:\n{state.architecture}" if state.architecture else ""

        return f"""Generate code for the following task:

Task Description: {state.task_description}{context_info}{arch_info}

Provide:
1. Complete, working code
2. Clear documentation
3. Error handling
4. Best practices implementation"""

    def _process_response(self, response: str, state: WorkflowState) -> Dict[str, Any]:
        return {"code": response}


class TestAgent(BaseAgent):
    """Agent responsible for generating tests."""

    def __init__(self):
        super().__init__(AgentType.TEST)

    def get_system_prompt(self) -> str:
        return """You are a Test Generation Agent. Your role is to:
1. Write comprehensive unit tests
2. Cover edge cases and error conditions
3. Follow TDD principles
4. Ensure high code coverage
5. Write clear and maintainable tests

Focus on thorough test coverage and quality."""

    def _prepare_user_message(self, state: WorkflowState) -> str:
        code_info = f"\n\nCode:\n{state.code}" if state.code else ""
        arch_info = f"\n\nArchitecture:\n{state.architecture}" if state.architecture else ""

        return f"""Generate tests for the following task:

Task Description: {state.task_description}{arch_info}{code_info}

Provide:
1. Comprehensive unit tests
2. Edge case coverage
3. Integration tests if needed
4. Clear test descriptions"""

    def _process_response(self, response: str, state: WorkflowState) -> Dict[str, Any]:
        return {"tests": response}


class ReviewAgent(BaseAgent):
    """Agent responsible for reviewing the solution."""

    def __init__(self):
        super().__init__(AgentType.REVIEW)

    def get_system_prompt(self) -> str:
        return """You are a Code Review Agent. Your role is to:
1. Review code quality and best practices
2. Verify test coverage and quality
3. Check for security vulnerabilities
4. Assess performance and scalability
5. Provide actionable feedback

Be thorough and constructive in your review."""

    def _prepare_user_message(self, state: WorkflowState) -> str:
        code_info = f"\n\nCode:\n{state.code}" if state.code else ""
        tests_info = f"\n\nTests:\n{state.tests}" if state.tests else ""

        return f"""Review the following solution:

Task Description: {state.task_description}{code_info}{tests_info}

Provide:
1. Code quality assessment
2. Test coverage analysis
3. Security review
4. Performance considerations
5. Recommended improvements"""

    def _process_response(self, response: str, state: WorkflowState) -> Dict[str, Any]:
        return {"review": response}
