"""
Aurea Orchestrator - Budget Service
Handles budget tracking and enforcement
"""
from datetime import date, datetime, timezone
from models import db, Organization, Budget, Job
import os


class BudgetService:
    """Service for managing organization budgets"""
    
    @staticmethod
    def get_default_daily_limit():
        """Get default daily budget limit from env"""
        return float(os.getenv('DEFAULT_DAILY_BUDGET_LIMIT', 1000.0))
    
    @staticmethod
    def get_default_monthly_limit():
        """Get default monthly budget limit from env"""
        return float(os.getenv('DEFAULT_MONTHLY_BUDGET_LIMIT', 30000.0))
    
    @staticmethod
    def get_default_mode():
        """Get default budget mode from env"""
        return os.getenv('DEFAULT_BUDGET_MODE', 'soft')
    
    @staticmethod
    def get_or_create_budget(org_id, period_type, period_date):
        """Get or create a budget record for the given period"""
        budget = Budget.query.filter_by(
            organization_id=org_id,
            period_type=period_type,
            period_date=period_date
        ).first()
        
        if not budget:
            budget = Budget(
                organization_id=org_id,
                period_type=period_type,
                period_date=period_date,
                amount_used=0.0
            )
            db.session.add(budget)
            db.session.commit()
        
        return budget
    
    @staticmethod
    def get_current_usage(org_id, period_type='daily'):
        """Get current budget usage for an organization"""
        today = date.today()
        
        if period_type == 'daily':
            period_date = today
        else:  # monthly
            period_date = today.replace(day=1)
        
        budget = BudgetService.get_or_create_budget(org_id, period_type, period_date)
        return budget.amount_used
    
    @staticmethod
    def get_budget_limit(organization, period_type='daily'):
        """Get the budget limit for an organization"""
        if period_type == 'daily':
            return organization.daily_budget_limit or BudgetService.get_default_daily_limit()
        else:  # monthly
            return organization.monthly_budget_limit or BudgetService.get_default_monthly_limit()
    
    @staticmethod
    def check_budget(org_id, estimated_cost=0.0):
        """
        Check if organization can run a job within budget
        Returns: (can_run: bool, reason: str, daily_usage: float, monthly_usage: float)
        """
        org = Organization.query.get(org_id)
        if not org:
            return False, "Organization not found", 0.0, 0.0
        
        # Get current usage
        daily_usage = BudgetService.get_current_usage(org_id, 'daily')
        monthly_usage = BudgetService.get_current_usage(org_id, 'monthly')
        
        # Get limits
        daily_limit = BudgetService.get_budget_limit(org, 'daily')
        monthly_limit = BudgetService.get_budget_limit(org, 'monthly')
        
        # Check if adding this job would exceed limits
        daily_would_exceed = (daily_usage + estimated_cost) > daily_limit
        monthly_would_exceed = (monthly_usage + estimated_cost) > monthly_limit
        
        # In soft mode, just warn
        if org.budget_mode == 'soft':
            if daily_would_exceed or monthly_would_exceed:
                reason = "Warning: Budget limit exceeded (soft mode - job will continue)"
                return True, reason, daily_usage, monthly_usage
            return True, "Within budget", daily_usage, monthly_usage
        
        # In hard mode, block if exceeded
        if daily_would_exceed:
            return False, "Daily budget limit exceeded", daily_usage, monthly_usage
        
        if monthly_would_exceed:
            return False, "Monthly budget limit exceeded", daily_usage, monthly_usage
        
        return True, "Within budget", daily_usage, monthly_usage
    
    @staticmethod
    def record_job_cost(org_id, job_id, cost):
        """Record the cost of a job to the budget"""
        today = date.today()
        
        # Update daily budget
        daily_budget = BudgetService.get_or_create_budget(org_id, 'daily', today)
        daily_budget.amount_used += cost
        
        # Update monthly budget
        monthly_date = today.replace(day=1)
        monthly_budget = BudgetService.get_or_create_budget(org_id, 'monthly', monthly_date)
        monthly_budget.amount_used += cost
        
        # Update job cost
        job = Job.query.get(job_id)
        if job:
            job.cost = cost
        
        db.session.commit()
    
    @staticmethod
    def get_billing_summary(org_id):
        """Get billing summary for an organization"""
        org = Organization.query.get(org_id)
        if not org:
            return None
        
        # Get current usage
        daily_usage = BudgetService.get_current_usage(org_id, 'daily')
        monthly_usage = BudgetService.get_current_usage(org_id, 'monthly')
        
        # Get limits
        daily_limit = BudgetService.get_budget_limit(org, 'daily')
        monthly_limit = BudgetService.get_budget_limit(org, 'monthly')
        
        # Get job stats
        total_jobs = Job.query.filter_by(organization_id=org_id).count()
        completed_jobs = Job.query.filter_by(organization_id=org_id, status='completed').count()
        failed_jobs = Job.query.filter_by(organization_id=org_id, status='failed').count()
        budget_exceeded_jobs = Job.query.filter_by(organization_id=org_id, status='budget_exceeded').count()
        
        return {
            'organization': org.to_dict(),
            'daily': {
                'usage': daily_usage,
                'limit': daily_limit,
                'percentage': (daily_usage / daily_limit * 100) if daily_limit > 0 else 0,
                'remaining': max(0, daily_limit - daily_usage)
            },
            'monthly': {
                'usage': monthly_usage,
                'limit': monthly_limit,
                'percentage': (monthly_usage / monthly_limit * 100) if monthly_limit > 0 else 0,
                'remaining': max(0, monthly_limit - monthly_usage)
            },
            'jobs': {
                'total': total_jobs,
                'completed': completed_jobs,
                'failed': failed_jobs,
                'budget_exceeded': budget_exceeded_jobs
            }
        }
