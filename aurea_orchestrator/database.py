"""Database configuration and models."""

from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

from aurea_orchestrator.config import settings

Base = declarative_base()


class Job(Base):
    """Job model for storing orchestrator tasks."""

    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(255), unique=True, index=True, nullable=False)
    task_description = Column(Text, nullable=False)
    status = Column(String(50), default="pending", nullable=False)
    result = Column(Text, nullable=True)
    metadata = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# Database engine and session
engine = create_engine(settings.database_url, echo=settings.debug if hasattr(settings, 'debug') else False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
