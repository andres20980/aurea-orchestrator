from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.auth import get_current_user, check_project_permission
from app.models.models import Job, User, Role
from app.schemas.schemas import JobCreate, JobUpdate, JobResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    job: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new job. Requires dev role on the project."""
    # Check permissions
    check_project_permission(job.project_id, current_user, db, Role.DEV)
    
    # Create job
    db_job = Job(**job.model_dump())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    
    return db_job


@router.get("/", response_model=List[JobResponse])
def list_jobs(
    project_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all jobs. Optionally filter by project_id."""
    if project_id:
        # Check permissions for specific project
        check_project_permission(project_id, current_user, db, Role.VIEWER)
        jobs = db.query(Job).filter(Job.project_id == project_id).all()
    else:
        # Get all jobs from projects user has access to
        from app.models.models import ProjectRole
        project_roles = db.query(ProjectRole).filter(ProjectRole.user_id == current_user.id).all()
        project_ids = [pr.project_id for pr in project_roles]
        jobs = db.query(Job).filter(Job.project_id.in_(project_ids)).all() if project_ids else []
    
    return jobs


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific job."""
    db_job = db.query(Job).filter(Job.id == job_id).first()
    if not db_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check permissions
    check_project_permission(db_job.project_id, current_user, db, Role.VIEWER)
    
    return db_job


@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_update: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a job. Requires dev role."""
    db_job = db.query(Job).filter(Job.id == job_id).first()
    if not db_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check permissions
    check_project_permission(db_job.project_id, current_user, db, Role.DEV)
    
    # Update only provided fields
    update_data = job_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_job, key, value)
    
    db.commit()
    db.refresh(db_job)
    
    return db_job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a job. Requires admin role."""
    db_job = db.query(Job).filter(Job.id == job_id).first()
    if not db_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check permissions
    check_project_permission(db_job.project_id, current_user, db, Role.ADMIN)
    
    db.delete(db_job)
    db.commit()
    
    return None
