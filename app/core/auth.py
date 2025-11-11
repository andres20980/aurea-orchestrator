from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.models import User, ProjectRole, Role

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user."""
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user


def check_project_permission(project_id: int, user: User, db: Session, min_role: Role = Role.VIEWER):
    """Check if user has minimum required role for a project."""
    role_hierarchy = {
        Role.VIEWER: 1,
        Role.DEV: 2,
        Role.ADMIN: 3
    }
    
    project_role = db.query(ProjectRole).filter(
        ProjectRole.project_id == project_id,
        ProjectRole.user_id == user.id
    ).first()
    
    if not project_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this project"
        )
    
    if role_hierarchy[project_role.role] < role_hierarchy[min_role]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Required: {min_role.value}, you have: {project_role.role.value}"
        )
    
    return project_role
