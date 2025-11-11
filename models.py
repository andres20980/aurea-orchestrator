"""
Aurea Orchestrator - Database Models
"""
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Organization(db.Model):
    """Organization model with budget tracking"""
    __tablename__ = 'organizations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Budget settings
    daily_budget_limit = db.Column(db.Float, nullable=True)  # None means use default
    monthly_budget_limit = db.Column(db.Float, nullable=True)  # None means use default
    budget_mode = db.Column(db.String(10), default='soft')  # 'soft' or 'hard'
    
    # Relationships
    budgets = db.relationship('Budget', back_populates='organization', cascade='all, delete-orphan')
    jobs = db.relationship('Job', back_populates='organization', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'daily_budget_limit': self.daily_budget_limit,
            'monthly_budget_limit': self.monthly_budget_limit,
            'budget_mode': self.budget_mode
        }


class Budget(db.Model):
    """Budget tracking for organizations"""
    __tablename__ = 'budgets'
    
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    
    # Period tracking
    period_type = db.Column(db.String(10), nullable=False)  # 'daily' or 'monthly'
    period_date = db.Column(db.Date, nullable=False)  # Date for the period
    
    # Budget amounts
    amount_used = db.Column(db.Float, default=0.0)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    organization = db.relationship('Organization', back_populates='budgets')
    
    # Unique constraint for org + period
    __table_args__ = (
        db.UniqueConstraint('organization_id', 'period_type', 'period_date', name='uix_org_period'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'period_type': self.period_type,
            'period_date': self.period_date.isoformat() if self.period_date else None,
            'amount_used': self.amount_used,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Job(db.Model):
    """Job execution tracking"""
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    
    name = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, running, completed, failed, budget_exceeded
    cost = db.Column(db.Float, default=0.0)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    organization = db.relationship('Organization', back_populates='jobs')
    
    def to_dict(self):
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'name': self.name,
            'status': self.status,
            'cost': self.cost,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
