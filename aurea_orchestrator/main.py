"""FastAPI application for Aurea Orchestrator."""

import uuid
from typing import Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from aurea_orchestrator.celery_app import celery_app, process_task
from aurea_orchestrator.schemas import TaskRequest, TaskResponse, TaskStatus

# Create FastAPI app
app = FastAPI(
    title="Aurea Orchestrator",
    description="Automated Unified Reasoning & Execution Agents - Multi-Agent Orchestration System",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Aurea Orchestrator",
        "version": "0.1.0",
        "description": "Multi-Agent Orchestration System",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/tasks", response_model=TaskResponse)
async def create_task(request: TaskRequest):
    """Create a new task for processing.

    Args:
        request: Task creation request

    Returns:
        Task response with task ID and status
    """
    # Generate unique task ID
    task_id = str(uuid.uuid4())

    # Submit task to Celery
    process_task.delay(task_id, request.description, request.metadata)

    return TaskResponse(task_id=task_id, status=TaskStatus.PENDING)


@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    """Get task status and results.

    Args:
        task_id: Task identifier

    Returns:
        Task response with current status and results
    """
    # Get task result from Celery
    result = celery_app.AsyncResult(task_id)

    if result.state == "PENDING":
        return TaskResponse(task_id=task_id, status=TaskStatus.PENDING)
    elif result.state == "STARTED":
        return TaskResponse(task_id=task_id, status=TaskStatus.IN_PROGRESS)
    elif result.state == "SUCCESS":
        return TaskResponse(
            task_id=task_id, status=TaskStatus.COMPLETED, result=result.result
        )
    elif result.state == "FAILURE":
        raise HTTPException(status_code=500, detail=f"Task failed: {str(result.info)}")
    else:
        return TaskResponse(task_id=task_id, status=TaskStatus.PENDING)


@app.get("/tasks/{task_id}/result")
async def get_task_result(task_id: str) -> Dict:
    """Get detailed task results.

    Args:
        task_id: Task identifier

    Returns:
        Detailed task results
    """
    result = celery_app.AsyncResult(task_id)

    if not result.ready():
        raise HTTPException(status_code=404, detail="Task not completed yet")

    if result.failed():
        raise HTTPException(status_code=500, detail=f"Task failed: {str(result.info)}")

    return result.result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
