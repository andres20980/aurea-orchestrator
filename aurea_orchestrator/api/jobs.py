"""API endpoints for jobs"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from aurea_orchestrator.models.config import get_db
from aurea_orchestrator.api.schemas import JobCreate, JobResponse
from aurea_orchestrator.services.prompt_service import JobService

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/", response_model=JobResponse, status_code=201)
def create_job(
    job: JobCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new job.
    
    If prompt_template_id is provided, the job will be associated with that template
    and the prompt version will be automatically recorded.
    """
    created_job = JobService.create_job(
        db=db,
        name=job.name,
        prompt_template_id=job.prompt_template_id,
        prompt_version=job.prompt_version,
        input_data=job.input_data
    )
    
    return created_job


@router.get("/", response_model=List[JobResponse])
def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    List all jobs.
    
    - **skip**: Number of jobs to skip (for pagination)
    - **limit**: Maximum number of jobs to return
    """
    jobs = JobService.list_jobs(db=db, skip=skip, limit=limit)
    return jobs


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific job by ID, including which prompt version was used."""
    job = JobService.get_job(db=db, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
