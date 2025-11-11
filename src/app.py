"""Main FastAPI application for the Aurea Orchestrator."""
from fastapi import FastAPI, Response
from fastapi.responses import PlainTextResponse
from typing import List
from .models import Job, JobStatus
from .storage import storage
from .export import export_approved_jobs_to_jsonl

app = FastAPI(
    title="Aurea Orchestrator",
    description="Automated Unified Reasoning & Execution Agents",
    version="1.0.0"
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Aurea Orchestrator",
        "description": "Automated Unified Reasoning & Execution Agents",
        "version": "1.0.0"
    }


@app.get("/jobs", response_model=List[Job])
async def list_jobs():
    """List all jobs."""
    return storage.get_all_jobs()


@app.get("/jobs/{job_id}", response_model=Job)
async def get_job(job_id: str):
    """Get a specific job by ID."""
    job = storage.get_job(job_id)
    if not job:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/jobs/status/{status}", response_model=List[Job])
async def list_jobs_by_status(status: JobStatus):
    """List jobs filtered by status."""
    all_jobs = storage.get_all_jobs()
    return [job for job in all_jobs if job.status == status]


@app.get("/export/trainset", response_class=PlainTextResponse)
async def export_trainset():
    """Export approved jobs as training data in JSONL format.
    
    Returns:
        JSONL formatted training data where each line contains:
        - prompt: The original task/question
        - solution: The approved solution
        - feedback: Review feedback (reviewer, rating, comments, approval status)
    
    This endpoint is designed for exporting data to fine-tune external LLMs.
    Only jobs with status=APPROVED and review feedback are included.
    """
    approved_jobs = storage.get_approved_jobs()
    jsonl_data = export_approved_jobs_to_jsonl(approved_jobs)
    
    return Response(
        content=jsonl_data,
        media_type="application/jsonl",
        headers={
            "Content-Disposition": "attachment; filename=trainset.jsonl"
        }
    )


@app.get("/stats")
async def get_stats():
    """Get statistics about jobs."""
    all_jobs = storage.get_all_jobs()
    
    stats = {
        "total_jobs": len(all_jobs),
        "by_status": {}
    }
    
    for status in JobStatus:
        count = len([job for job in all_jobs if job.status == status])
        stats["by_status"][status.value] = count
    
    approved_jobs = storage.get_approved_jobs()
    stats["approved_with_feedback"] = len(approved_jobs)
    
    return stats
