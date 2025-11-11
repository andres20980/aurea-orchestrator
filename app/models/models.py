from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class Role(str, enum.Enum):
    """Project roles for RBAC."""
    VIEWER = "viewer"
    DEV = "dev"
    ADMIN = "admin"


class User(Base):
    """User model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project_roles = relationship("ProjectRole", back_populates="user")


class Project(Base):
    """Project model."""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    jobs = relationship("Job", back_populates="project", cascade="all, delete-orphan")
    project_roles = relationship("ProjectRole", back_populates="project", cascade="all, delete-orphan")


class ProjectRole(Base):
    """Project role assignment for RBAC."""
    __tablename__ = "project_roles"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(SQLEnum(Role), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="project_roles")
    user = relationship("User", back_populates="project_roles")


class Job(Base):
    """Job model."""
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, default="pending")
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="jobs")
    metrics = relationship("Metric", back_populates="job", cascade="all, delete-orphan")
    costs = relationship("Cost", back_populates="job", cascade="all, delete-orphan")


class Metric(Base):
    """Metric model."""
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    job = relationship("Job", back_populates="metrics")


class Cost(Base):
    """Cost model."""
    __tablename__ = "costs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    description = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    job = relationship("Job", back_populates="costs")
