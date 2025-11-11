from typing import Literal, Annotated, Sequence
from langgraph.graph import StateGraph, END, START
from models import WorkflowState, ReviewDecision, NodeStatus
from storage import job_store
import operator
import time


def plan_node(state: WorkflowState) -> WorkflowState:
    """Plan phase: Generate implementation plan"""
    job_id = state["job_id"]
    job_store.add_node_progress(job_id, "plan", NodeStatus.RUNNING)
    
    try:
        # Simulate planning work
        time.sleep(0.5)
        input_data = state["input_data"]
        plan_output = f"Plan created for: {input_data.get('task', 'unknown task')}"
        
        state["plan_output"] = plan_output
        state["current_node"] = "plan"
        
        job_store.add_node_progress(job_id, "plan", NodeStatus.COMPLETED, output=plan_output)
    except Exception as e:
        state["error"] = str(e)
        job_store.add_node_progress(job_id, "plan", NodeStatus.FAILED, error=str(e))
    
    return state


def implement_node(state: WorkflowState) -> WorkflowState:
    """Implementation phase: Execute the plan"""
    job_id = state["job_id"]
    job_store.add_node_progress(job_id, "implement", NodeStatus.RUNNING)
    
    try:
        # Simulate implementation work
        time.sleep(0.5)
        plan = state.get("plan_output", "")
        implement_output = f"Implementation completed based on: {plan}"
        
        state["implement_output"] = implement_output
        state["current_node"] = "implement"
        
        job_store.add_node_progress(job_id, "implement", NodeStatus.COMPLETED, output=implement_output)
    except Exception as e:
        state["error"] = str(e)
        job_store.add_node_progress(job_id, "implement", NodeStatus.FAILED, error=str(e))
    
    return state


def test_node(state: WorkflowState) -> WorkflowState:
    """Testing phase: Run tests on implementation"""
    job_id = state["job_id"]
    job_store.add_node_progress(job_id, "test", NodeStatus.RUNNING)
    
    try:
        # Simulate testing work
        time.sleep(0.5)
        implementation = state.get("implement_output", "")
        test_output = f"Tests passed for: {implementation}"
        
        state["test_output"] = test_output
        state["current_node"] = "test"
        
        job_store.add_node_progress(job_id, "test", NodeStatus.COMPLETED, output=test_output)
    except Exception as e:
        state["error"] = str(e)
        job_store.add_node_progress(job_id, "test", NodeStatus.FAILED, error=str(e))
    
    return state


def review_precheck_node(state: WorkflowState) -> WorkflowState:
    """Review precheck phase: Preliminary review checks"""
    job_id = state["job_id"]
    job_store.add_node_progress(job_id, "review_precheck", NodeStatus.RUNNING)
    
    try:
        # Simulate review precheck work
        time.sleep(0.5)
        implementation = state.get("implement_output", "")
        review_precheck_output = f"Precheck completed for: {implementation}"
        
        state["review_precheck_output"] = review_precheck_output
        state["current_node"] = "review_precheck"
        
        job_store.add_node_progress(job_id, "review_precheck", NodeStatus.COMPLETED, output=review_precheck_output)
    except Exception as e:
        state["error"] = str(e)
        job_store.add_node_progress(job_id, "review_precheck", NodeStatus.FAILED, error=str(e))
    
    return state


def combined_parallel_node(state: WorkflowState) -> WorkflowState:
    """Combined node that runs test and review_precheck in sequence (simulating parallel)"""
    # Run test
    state = test_node(state)
    # Run review_precheck
    state = review_precheck_node(state)
    return state


def review_node(state: WorkflowState) -> WorkflowState:
    """Review phase: Final review and decision"""
    job_id = state["job_id"]
    job_store.add_node_progress(job_id, "review", NodeStatus.RUNNING)
    
    try:
        # Simulate review work
        time.sleep(0.5)
        test_output = state.get("test_output", "")
        precheck_output = state.get("review_precheck_output", "")
        
        # Simple logic: approve on first iteration, reject on second, approve on third
        iteration = state["iteration_count"]
        if iteration == 0:
            decision = ReviewDecision.APPROVED
            review_output = f"APPROVED: {test_output} and {precheck_output}"
        elif iteration < state["max_iterations"] - 1:
            decision = ReviewDecision.REJECTED
            review_output = f"REJECTED: Needs improvement. {test_output}"
        else:
            decision = ReviewDecision.APPROVED
            review_output = f"APPROVED: Final approval after {iteration + 1} iterations"
        
        state["review_output"] = review_output
        state["review_decision"] = decision
        state["current_node"] = "review"
        state["iteration_count"] = iteration + 1
        
        job_store.add_node_progress(job_id, "review", NodeStatus.COMPLETED, output=review_output)
    except Exception as e:
        state["error"] = str(e)
        job_store.add_node_progress(job_id, "review", NodeStatus.FAILED, error=str(e))
    
    return state


def should_continue(state: WorkflowState) -> Literal["plan", "end"]:
    """Decide whether to loop back or end based on review decision"""
    decision = state.get("review_decision")
    iteration = state.get("iteration_count", 0)
    max_iterations = state.get("max_iterations", 3)
    
    # End if approved or max iterations reached
    if decision == ReviewDecision.APPROVED or iteration >= max_iterations:
        return "end"
    
    # Loop back to plan phase
    return "plan"


def create_workflow() -> StateGraph:
    """Create the LangGraph workflow
    
    The workflow follows this pattern:
    plan → implement → test_and_review_precheck → review
    
    Note: test and review_precheck are executed sequentially within a single node
    to work around LangGraph's limitation on multiple outgoing edges.
    In a production environment with proper LangGraph setup, these could be
    truly parallel using Send API or other mechanisms.
    """
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("plan", plan_node)
    workflow.add_node("implement", implement_node)
    workflow.add_node("test_and_review_precheck", combined_parallel_node)
    workflow.add_node("review", review_node)
    
    # Set entry point
    workflow.set_entry_point("plan")
    
    # Define edges
    workflow.add_edge("plan", "implement")
    workflow.add_edge("implement", "test_and_review_precheck")
    workflow.add_edge("test_and_review_precheck", "review")
    
    # Conditional edge from review
    workflow.add_conditional_edges(
        "review",
        should_continue,
        {
            "plan": "plan",
            "end": END,
        }
    )
    
    return workflow.compile()
