from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from app.models.models import Role


# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Project schemas
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ProjectRole schemas
class ProjectRoleBase(BaseModel):
    user_id: int
    role: Role


class ProjectRoleCreate(ProjectRoleBase):
    pass


class ProjectRoleResponse(ProjectRoleBase):
    id: int
    project_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Job schemas
class JobBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: Optional[str] = "pending"


class JobCreate(JobBase):
    project_id: int


class JobUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class JobResponse(JobBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Metric schemas
class MetricBase(BaseModel):
    name: str
    value: float
    unit: Optional[str] = None


class MetricCreate(MetricBase):
    job_id: int


class MetricResponse(MetricBase):
    id: int
    job_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True


# Cost schemas
class CostBase(BaseModel):
    amount: float
    currency: str = "USD"
    description: Optional[str] = None


class CostCreate(CostBase):
    job_id: int


class CostResponse(CostBase):
    id: int
    job_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True


# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
