from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.auth import get_current_user, check_project_permission
from app.models.models import Metric, Job, User, Role
from app.schemas.schemas import MetricCreate, MetricResponse

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.post("/", response_model=MetricResponse, status_code=status.HTTP_201_CREATED)
def create_metric(
    metric: MetricCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new metric. Requires dev role on the job's project."""
    # Get job to check project
    job = db.query(Job).filter(Job.id == metric.job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check permissions
    check_project_permission(job.project_id, current_user, db, Role.DEV)
    
    # Create metric
    db_metric = Metric(**metric.model_dump())
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    
    return db_metric


@router.get("/", response_model=List[MetricResponse])
def list_metrics(
    job_id: int = None,
    project_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List metrics. Filter by job_id or project_id."""
    if job_id:
        # Get job to check project
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        # Check permissions
        check_project_permission(job.project_id, current_user, db, Role.VIEWER)
        metrics = db.query(Metric).filter(Metric.job_id == job_id).all()
    elif project_id:
        # Check permissions
        check_project_permission(project_id, current_user, db, Role.VIEWER)
        
        # Get all jobs in project
        jobs = db.query(Job).filter(Job.project_id == project_id).all()
        job_ids = [j.id for j in jobs]
        metrics = db.query(Metric).filter(Metric.job_id.in_(job_ids)).all() if job_ids else []
    else:
        # Get all metrics from projects user has access to
        from app.models.models import ProjectRole
        project_roles = db.query(ProjectRole).filter(ProjectRole.user_id == current_user.id).all()
        project_ids = [pr.project_id for pr in project_roles]
        
        jobs = db.query(Job).filter(Job.project_id.in_(project_ids)).all() if project_ids else []
        job_ids = [j.id for j in jobs]
        metrics = db.query(Metric).filter(Metric.job_id.in_(job_ids)).all() if job_ids else []
    
    return metrics


@router.get("/{metric_id}", response_model=MetricResponse)
def get_metric(
    metric_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific metric."""
    db_metric = db.query(Metric).filter(Metric.id == metric_id).first()
    if not db_metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Metric not found"
        )
    
    # Get job to check project
    job = db.query(Job).filter(Job.id == db_metric.job_id).first()
    
    # Check permissions
    check_project_permission(job.project_id, current_user, db, Role.VIEWER)
    
    return db_metric


@router.delete("/{metric_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_metric(
    metric_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a metric. Requires admin role."""
    db_metric = db.query(Metric).filter(Metric.id == metric_id).first()
    if not db_metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Metric not found"
        )
    
    # Get job to check project
    job = db.query(Job).filter(Job.id == db_metric.job_id).first()
    
    # Check permissions
    check_project_permission(job.project_id, current_user, db, Role.ADMIN)
    
    db.delete(db_metric)
    db.commit()
    
    return None
