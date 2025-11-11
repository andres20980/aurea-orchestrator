from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.auth import get_current_user, check_project_permission
from app.models.models import Project, ProjectRole, User, Role
from app.schemas.schemas import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectRoleCreate, ProjectRoleResponse

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new project and assign the creator as admin."""
    # Check if project name already exists
    existing = db.query(Project).filter(Project.name == project.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project with this name already exists"
        )
    
    # Create project
    db_project = Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    # Assign creator as admin
    project_role = ProjectRole(
        project_id=db_project.id,
        user_id=current_user.id,
        role=Role.ADMIN
    )
    db.add(project_role)
    db.commit()
    
    return db_project


@router.get("/", response_model=List[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all projects the current user has access to."""
    # Get all project IDs the user has access to
    project_roles = db.query(ProjectRole).filter(ProjectRole.user_id == current_user.id).all()
    project_ids = [pr.project_id for pr in project_roles]
    
    # Get projects
    projects = db.query(Project).filter(Project.id.in_(project_ids)).all() if project_ids else []
    
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific project."""
    # Check permissions
    check_project_permission(project_id, current_user, db, Role.VIEWER)
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a project. Requires admin role."""
    # Check permissions
    check_project_permission(project_id, current_user, db, Role.ADMIN)
    
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Update only provided fields
    update_data = project_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_project, key, value)
    
    db.commit()
    db.refresh(db_project)
    
    return db_project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a project. Requires admin role."""
    # Check permissions
    check_project_permission(project_id, current_user, db, Role.ADMIN)
    
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    db.delete(db_project)
    db.commit()
    
    return None


@router.post("/{project_id}/roles", response_model=ProjectRoleResponse, status_code=status.HTTP_201_CREATED)
def assign_project_role(
    project_id: int,
    role_create: ProjectRoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assign a role to a user for a project. Requires admin role."""
    # Check permissions
    check_project_permission(project_id, current_user, db, Role.ADMIN)
    
    # Check if project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if user already has a role for this project
    existing_role = db.query(ProjectRole).filter(
        ProjectRole.project_id == project_id,
        ProjectRole.user_id == role_create.user_id
    ).first()
    
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a role for this project"
        )
    
    # Create role assignment
    project_role = ProjectRole(
        project_id=project_id,
        user_id=role_create.user_id,
        role=role_create.role
    )
    db.add(project_role)
    db.commit()
    db.refresh(project_role)
    
    return project_role


@router.get("/{project_id}/roles", response_model=List[ProjectRoleResponse])
def list_project_roles(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all role assignments for a project. Requires viewer role."""
    # Check permissions
    check_project_permission(project_id, current_user, db, Role.VIEWER)
    
    roles = db.query(ProjectRole).filter(ProjectRole.project_id == project_id).all()
    return roles


@router.delete("/{project_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_project_role(
    project_id: int,
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a role assignment. Requires admin role."""
    # Check permissions
    check_project_permission(project_id, current_user, db, Role.ADMIN)
    
    role = db.query(ProjectRole).filter(
        ProjectRole.id == role_id,
        ProjectRole.project_id == project_id
    ).first()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role assignment not found"
        )
    
    db.delete(role)
    db.commit()
    
    return None
