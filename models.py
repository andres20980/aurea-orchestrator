"""
Database models for the aurea-orchestrator monitoring system.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, create_engine, func
from sqlalchemy.orm import declarative_base, sessionmaker
import os

Base = declarative_base()


class Metric(Base):
    """
    Metrics table to store task execution metrics.
    """
    __tablename__ = 'metrics'

    id = Column(Integer, primary_key=True)
    job_id = Column(String(255), nullable=False, index=True)
    task_name = Column(String(255), nullable=False)
    model_used = Column(String(255), nullable=False)
    token_count = Column(Integer, nullable=False)
    latency_ms = Column(Float, nullable=False)
    cost_estimate = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(datetime.UTC), nullable=False)

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'job_id': self.job_id,
            'task_name': self.task_name,
            'model_used': self.model_used,
            'token_count': self.token_count,
            'latency_ms': self.latency_ms,
            'cost_estimate': self.cost_estimate,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


def get_engine():
    """Get database engine."""
    database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/aurea_orchestrator')
    return create_engine(database_url)


def init_db():
    """Initialize database tables."""
    engine = get_engine()
    Base.metadata.create_all(engine)


def get_session():
    """Get database session."""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def get_job_stats(job_id):
    """
    Get aggregated statistics for a specific job.
    
    Args:
        job_id: The job identifier
        
    Returns:
        Dictionary containing aggregated stats
    """
    session = get_session()
    try:
        stats = session.query(
            func.count(Metric.id).label('total_tasks'),
            func.sum(Metric.token_count).label('total_tokens'),
            func.sum(Metric.latency_ms).label('total_latency_ms'),
            func.avg(Metric.latency_ms).label('avg_latency_ms'),
            func.sum(Metric.cost_estimate).label('total_cost'),
            func.avg(Metric.cost_estimate).label('avg_cost')
        ).filter(Metric.job_id == job_id).first()
        
        # Get task breakdown
        task_breakdown = session.query(
            Metric.task_name,
            func.count(Metric.id).label('count'),
            func.avg(Metric.latency_ms).label('avg_latency'),
            func.sum(Metric.cost_estimate).label('total_cost')
        ).filter(Metric.job_id == job_id).group_by(Metric.task_name).all()
        
        # Get model usage
        model_usage = session.query(
            Metric.model_used,
            func.count(Metric.id).label('count'),
            func.sum(Metric.token_count).label('total_tokens'),
            func.sum(Metric.cost_estimate).label('total_cost')
        ).filter(Metric.job_id == job_id).group_by(Metric.model_used).all()
        
        return {
            'job_id': job_id,
            'total_tasks': stats.total_tasks or 0,
            'total_tokens': stats.total_tokens or 0,
            'total_latency_ms': stats.total_latency_ms or 0.0,
            'avg_latency_ms': float(stats.avg_latency_ms) if stats.avg_latency_ms else 0.0,
            'total_cost': stats.total_cost or 0.0,
            'avg_cost': float(stats.avg_cost) if stats.avg_cost else 0.0,
            'task_breakdown': [
                {
                    'task_name': t.task_name,
                    'count': t.count,
                    'avg_latency_ms': float(t.avg_latency),
                    'total_cost': float(t.total_cost)
                } for t in task_breakdown
            ],
            'model_usage': [
                {
                    'model': m.model_used,
                    'count': m.count,
                    'total_tokens': m.total_tokens,
                    'total_cost': float(m.total_cost)
                } for m in model_usage
            ]
        }
    finally:
        session.close()
