"""SQLAlchemy models for storing evaluation results in Postgres"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Text, Enum
from sqlalchemy.orm import declarative_base, relationship
import enum

Base = declarative_base()


class EvalStatus(enum.Enum):
    """Status of an evaluation run"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class EvalRun(Base):
    """Represents a complete evaluation run"""
    __tablename__ = "eval_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String(64), unique=True, index=True, nullable=False)
    status = Column(Enum(EvalStatus), default=EvalStatus.PENDING, nullable=False)
    feature_type = Column(String(100), nullable=True)  # Optional filter by feature
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    total_cases = Column(Integer, default=0)
    passed_cases = Column(Integer, default=0)
    failed_cases = Column(Integer, default=0)
    average_accuracy = Column(Float, nullable=True)
    average_latency = Column(Float, nullable=True)
    total_cost = Column(Float, nullable=True)
    run_metadata = Column(JSON, nullable=True)

    # Relationship to individual results
    results = relationship("EvalResult", back_populates="run", cascade="all, delete-orphan")


class EvalResult(Base):
    """Stores individual evaluation result for a single test case"""
    __tablename__ = "eval_results"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("eval_runs.id"), nullable=False, index=True)
    case_id = Column(String(100), nullable=False, index=True)
    feature_type = Column(String(100), nullable=False, index=True)
    test_type = Column(String(50), nullable=False)  # "golden" or "regression"
    
    # Test details
    input_data = Column(JSON, nullable=False)
    expected_output = Column(JSON, nullable=False)
    actual_output = Column(JSON, nullable=True)
    
    # Scorecard metrics
    passed = Column(Integer, nullable=False)  # 1 for pass, 0 for fail
    accuracy = Column(Float, nullable=True)
    latency_ms = Column(Float, nullable=True)
    cost = Column(Float, nullable=True)
    
    # Additional info
    error_message = Column(Text, nullable=True)
    executed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    result_metadata = Column(JSON, nullable=True)

    # Relationship
    run = relationship("EvalRun", back_populates="results")
