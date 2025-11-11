from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime
from models import JobStatus, JobResponse, JobStatusResponse
from storage import job_store
from workflow import create_workflow
import asyncio


app = FastAPI(title="Aurea Orchestrator", version="1.0.0")

# Create workflow
workflow_graph = create_workflow()


class CreateJobRequest(BaseModel):
    """Request model for creating a job"""
    input_data: Dict
    max_iterations: Optional[int] = 3


class CreateJobResponse(BaseModel):
    """Response model for job creation"""
    job_id: str
    status: str
    created_at: datetime


class NodeProgressResponse(BaseModel):
    """Node progress response model"""
    node_name: str
    status: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    output: Optional[str]
    error: Optional[str]


class JobStatusDetailResponse(BaseModel):
    """Detailed job status response"""
    job_id: str
    status: str
    current_node: Optional[str]
    iteration_count: int
    max_iterations: int
    node_progress: list
    created_at: datetime
    updated_at: datetime


def run_workflow(job_id: str):
    """Run the workflow for a job"""
    try:
        job = job_store.get_job(job_id)
        if not job:
            return
        
        # Update job status to running
        job_store.update_job_status(job_id, JobStatus.RUNNING)
        
        # Get initial state
        state = job["state"]
        
        # Run the workflow
        final_state = workflow_graph.invoke(state)
        
        # Update final state
        job_store.update_job_state(job_id, final_state)
        
        # Update job status based on outcome
        if final_state.get("error"):
            job_store.update_job_status(job_id, JobStatus.FAILED)
        else:
            job_store.update_job_status(job_id, JobStatus.COMPLETED)
    
    except Exception as e:
        job_store.update_job_status(job_id, JobStatus.FAILED)
        if job_id in job_store.jobs:
            job_store.jobs[job_id]["state"]["error"] = str(e)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Aurea Orchestrator",
        "description": "Automated Unified Reasoning & Execution Agents",
        "version": "1.0.0",
        "endpoints": {
            "create_job": "POST /jobs",
            "get_job_status": "GET /jobs/{id}/status"
        }
    }


@app.post("/jobs", response_model=CreateJobResponse)
async def create_job(request: CreateJobRequest, background_tasks: BackgroundTasks):
    """Create a new job and start workflow execution"""
    # Create job in store
    job_id = job_store.create_job(
        input_data=request.input_data,
        max_iterations=request.max_iterations
    )
    
    # Start workflow in background
    background_tasks.add_task(run_workflow, job_id)
    
    # Return job info
    job = job_store.get_job(job_id)
    return CreateJobResponse(
        job_id=job_id,
        status=job["status"],
        created_at=job["created_at"]
    )


@app.get("/jobs/{job_id}/status", response_model=JobStatusDetailResponse)
async def get_job_status(job_id: str):
    """Get the current status of a job, including progress of each node"""
    status = job_store.get_job_status(job_id)
    
    if not status:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    return JobStatusDetailResponse(
        job_id=status["job_id"],
        status=status["status"],
        current_node=status["current_node"],
        iteration_count=status["iteration_count"],
        max_iterations=status["max_iterations"],
        node_progress=status["node_progress"],
        created_at=status["created_at"],
        updated_at=status["updated_at"]
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
