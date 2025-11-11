from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.auth import get_current_user, check_project_permission
from app.models.models import Cost, Job, User, Role
from app.schemas.schemas import CostCreate, CostResponse

router = APIRouter(prefix="/costs", tags=["costs"])


@router.post("/", response_model=CostResponse, status_code=status.HTTP_201_CREATED)
def create_cost(
    cost: CostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new cost entry. Requires dev role on the job's project."""
    # Get job to check project
    job = db.query(Job).filter(Job.id == cost.job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check permissions
    check_project_permission(job.project_id, current_user, db, Role.DEV)
    
    # Create cost
    db_cost = Cost(**cost.model_dump())
    db.add(db_cost)
    db.commit()
    db.refresh(db_cost)
    
    return db_cost


@router.get("/", response_model=List[CostResponse])
def list_costs(
    job_id: int = None,
    project_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List costs. Filter by job_id or project_id."""
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
        costs = db.query(Cost).filter(Cost.job_id == job_id).all()
    elif project_id:
        # Check permissions
        check_project_permission(project_id, current_user, db, Role.VIEWER)
        
        # Get all jobs in project
        jobs = db.query(Job).filter(Job.project_id == project_id).all()
        job_ids = [j.id for j in jobs]
        costs = db.query(Cost).filter(Cost.job_id.in_(job_ids)).all() if job_ids else []
    else:
        # Get all costs from projects user has access to
        from app.models.models import ProjectRole
        project_roles = db.query(ProjectRole).filter(ProjectRole.user_id == current_user.id).all()
        project_ids = [pr.project_id for pr in project_roles]
        
        jobs = db.query(Job).filter(Job.project_id.in_(project_ids)).all() if project_ids else []
        job_ids = [j.id for j in jobs]
        costs = db.query(Cost).filter(Cost.job_id.in_(job_ids)).all() if job_ids else []
    
    return costs


@router.get("/{cost_id}", response_model=CostResponse)
def get_cost(
    cost_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific cost entry."""
    db_cost = db.query(Cost).filter(Cost.id == cost_id).first()
    if not db_cost:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cost not found"
        )
    
    # Get job to check project
    job = db.query(Job).filter(Job.id == db_cost.job_id).first()
    
    # Check permissions
    check_project_permission(job.project_id, current_user, db, Role.VIEWER)
    
    return db_cost


@router.delete("/{cost_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cost(
    cost_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a cost entry. Requires admin role."""
    db_cost = db.query(Cost).filter(Cost.id == cost_id).first()
    if not db_cost:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cost not found"
        )
    
    # Get job to check project
    job = db.query(Job).filter(Job.id == db_cost.job_id).first()
    
    # Check permissions
    check_project_permission(job.project_id, current_user, db, Role.ADMIN)
    
    db.delete(db_cost)
    db.commit()
    
    return None
