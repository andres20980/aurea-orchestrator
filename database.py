"""
Database models for the meta-learning system.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone
import json

Base = declarative_base()


class ReviewFeedback(Base):
    """Store review feedback for model routing decisions."""
    __tablename__ = 'review_feedback'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    input_text = Column(Text, nullable=False)
    selected_model = Column(String(100), nullable=False)
    success = Column(Boolean, nullable=False)
    execution_time = Column(Float)
    confidence_score = Column(Float)
    features = Column(Text)  # JSON-encoded features
    
    def get_features_dict(self):
        """Parse features from JSON string."""
        if self.features:
            return json.loads(self.features)
        return {}
    
    def set_features_dict(self, features_dict):
        """Store features as JSON string."""
        self.features = json.dumps(features_dict)


class RouterMetrics(Base):
    """Store router performance metrics over time."""
    __tablename__ = 'router_metrics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    accuracy = Column(Float, nullable=False)
    total_predictions = Column(Integer, nullable=False)
    successful_predictions = Column(Integer, nullable=False)
    version = Column(Integer, default=1, nullable=False)


class Database:
    """Database manager for the meta-learning system."""
    
    def __init__(self, db_url="sqlite:///router_feedback.db"):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def add_feedback(self, input_text, selected_model, success, execution_time=None, 
                     confidence_score=None, features=None):
        """Add new feedback to the database."""
        feedback = ReviewFeedback(
            input_text=input_text,
            selected_model=selected_model,
            success=success,
            execution_time=execution_time,
            confidence_score=confidence_score
        )
        if features:
            feedback.set_features_dict(features)
        self.session.add(feedback)
        self.session.commit()
        return feedback
    
    def get_all_feedback(self):
        """Get all feedback records."""
        return self.session.query(ReviewFeedback).all()
    
    def get_feedback_by_model(self, model_name):
        """Get feedback for a specific model."""
        return self.session.query(ReviewFeedback).filter(
            ReviewFeedback.selected_model == model_name
        ).all()
    
    def add_metrics(self, accuracy, total_predictions, successful_predictions, version=1):
        """Add router metrics."""
        metrics = RouterMetrics(
            accuracy=accuracy,
            total_predictions=total_predictions,
            successful_predictions=successful_predictions,
            version=version
        )
        self.session.add(metrics)
        self.session.commit()
        return metrics
    
    def get_latest_metrics(self):
        """Get the most recent metrics."""
        return self.session.query(RouterMetrics).order_by(
            RouterMetrics.timestamp.desc()
        ).first()
    
    def get_all_metrics(self):
        """Get all metrics records."""
        return self.session.query(RouterMetrics).order_by(
            RouterMetrics.timestamp.asc()
        ).all()
    
    def close(self):
        """Close database session."""
        self.session.close()
