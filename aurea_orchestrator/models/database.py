"""Database models for Aurea Orchestrator"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class PromptTemplate(Base):
    """Prompt template with versioning support"""
    
    __tablename__ = "prompt_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    version = Column(Integer, nullable=False, default=1)
    description = Column(Text, nullable=True)
    template_yaml = Column(Text, nullable=False)
    variables = Column(JSON, nullable=True)  # JSON list of required variables
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_active = Column(Integer, default=1, nullable=False)  # SQLite doesn't have boolean
    
    # Relationship to jobs
    jobs = relationship("Job", back_populates="prompt_template")
    
    def __repr__(self):
        return f"<PromptTemplate(name='{self.name}', version={self.version})>"


class Job(Base):
    """Job execution tracking"""
    
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    prompt_template_id = Column(Integer, ForeignKey("prompt_templates.id"), nullable=True)
    prompt_version = Column(Integer, nullable=True)
    status = Column(String(50), nullable=False, default="pending")
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationship to prompt template
    prompt_template = relationship("PromptTemplate", back_populates="jobs")
    
    def __repr__(self):
        return f"<Job(name='{self.name}', status='{self.status}')>"
