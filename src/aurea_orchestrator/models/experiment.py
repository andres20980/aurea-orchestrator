"""Database models for experiments"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Experiment(Base):
    """Represents an experiment comparing multiple agent configurations"""
    
    __tablename__ = "experiments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    feature_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    runs = relationship("ExperimentRun", back_populates="experiment", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Experiment(id={self.id}, name='{self.name}', feature='{self.feature_name}')>"


class AgentConfiguration(Base):
    """Represents a specific agent configuration (e.g., Architect v1, v2)"""
    
    __tablename__ = "agent_configurations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    version = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    config_params = Column(JSON, nullable=True)  # Store configuration as JSON
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    runs = relationship("ExperimentRun", back_populates="agent_config")
    
    def __repr__(self):
        return f"<AgentConfiguration(id={self.id}, name='{self.name}', version='{self.version}')>"


class ExperimentRun(Base):
    """Represents a single run of an experiment with a specific agent configuration"""
    
    __tablename__ = "experiment_runs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id"), nullable=False)
    agent_config_id = Column(Integer, ForeignKey("agent_configurations.id"), nullable=False)
    
    # Metrics
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    latency_ms = Column(Float, nullable=True)  # Execution time in milliseconds
    cost = Column(Float, nullable=True)  # Cost in USD
    quality_score = Column(Float, nullable=True)  # Quality metric (0-100)
    
    # Results
    output = Column(JSON, nullable=True)  # Agent output
    metrics = Column(JSON, nullable=True)  # Additional custom metrics
    error = Column(Text, nullable=True)  # Error message if run failed
    status = Column(String(50), default="pending", nullable=False)  # pending, running, completed, failed
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    experiment = relationship("Experiment", back_populates="runs")
    agent_config = relationship("AgentConfiguration", back_populates="runs")
    
    def __repr__(self):
        return f"<ExperimentRun(id={self.id}, experiment_id={self.experiment_id}, status='{self.status}')>"
