"""
Tests for Aurea Orchestrator Budget Management
"""
import pytest
from datetime import date, datetime, timezone
from app import app
from models import db, Organization, Budget, Job
from budget_service import BudgetService
import os


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()


@pytest.fixture
def sample_org():
    """Create a sample organization"""
    org = Organization(
        name="Test Org",
        daily_budget_limit=100.0,
        monthly_budget_limit=3000.0,
        budget_mode='soft'
    )
    db.session.add(org)
    db.session.commit()
    return org


class TestBudgetService:
    """Test BudgetService functionality"""
    
    def test_get_default_limits(self):
        """Test default limit retrieval from environment"""
        # Save original values
        original_daily = os.getenv('DEFAULT_DAILY_BUDGET_LIMIT')
        original_monthly = os.getenv('DEFAULT_MONTHLY_BUDGET_LIMIT')
        
        # Test defaults
        daily = BudgetService.get_default_daily_limit()
        monthly = BudgetService.get_default_monthly_limit()
        
        assert isinstance(daily, float)
        assert isinstance(monthly, float)
        assert daily > 0
        assert monthly > 0
    
    def test_get_or_create_budget(self, client, sample_org):
        """Test budget record creation"""
        with app.app_context():
            today = date.today()
            
            # Create daily budget
            budget = BudgetService.get_or_create_budget(
                sample_org.id, 'daily', today
            )
            
            assert budget is not None
            assert budget.organization_id == sample_org.id
            assert budget.period_type == 'daily'
            assert budget.period_date == today
            assert budget.amount_used == 0.0
            
            # Retrieve same budget (should not create new one)
            budget2 = BudgetService.get_or_create_budget(
                sample_org.id, 'daily', today
            )
            
            assert budget.id == budget2.id
    
    def test_get_current_usage(self, client, sample_org):
        """Test current usage retrieval"""
        with app.app_context():
            # Initially should be 0
            usage = BudgetService.get_current_usage(sample_org.id, 'daily')
            assert usage == 0.0
            
            # Add some usage
            today = date.today()
            budget = BudgetService.get_or_create_budget(
                sample_org.id, 'daily', today
            )
            budget.amount_used = 50.0
            db.session.commit()
            
            # Check usage again
            usage = BudgetService.get_current_usage(sample_org.id, 'daily')
            assert usage == 50.0
    
    def test_check_budget_soft_mode(self, client, sample_org):
        """Test budget checking in soft mode"""
        with app.app_context():
            # Within budget
            can_run, reason, daily, monthly = BudgetService.check_budget(
                sample_org.id, 50.0
            )
            assert can_run is True
            assert "Within budget" in reason
            
            # Exceeding budget (soft mode allows it)
            can_run, reason, daily, monthly = BudgetService.check_budget(
                sample_org.id, 150.0
            )
            assert can_run is True
            assert "Warning" in reason or "soft mode" in reason.lower()
    
    def test_check_budget_hard_mode(self, client, sample_org):
        """Test budget checking in hard mode"""
        with app.app_context():
            # Switch to hard mode
            sample_org.budget_mode = 'hard'
            db.session.commit()
            
            # Within budget
            can_run, reason, daily, monthly = BudgetService.check_budget(
                sample_org.id, 50.0
            )
            assert can_run is True
            assert "Within budget" in reason
            
            # Exceeding budget (hard mode blocks it)
            can_run, reason, daily, monthly = BudgetService.check_budget(
                sample_org.id, 150.0
            )
            assert can_run is False
            assert "exceeded" in reason.lower()
    
    def test_record_job_cost(self, client, sample_org):
        """Test recording job costs to budget"""
        with app.app_context():
            # Create a job
            job = Job(
                organization_id=sample_org.id,
                name="Test Job",
                status="completed"
            )
            db.session.add(job)
            db.session.commit()
            
            # Record cost
            BudgetService.record_job_cost(sample_org.id, job.id, 25.0)
            
            # Check daily usage
            daily_usage = BudgetService.get_current_usage(sample_org.id, 'daily')
            assert daily_usage == 25.0
            
            # Check monthly usage
            monthly_usage = BudgetService.get_current_usage(sample_org.id, 'monthly')
            assert monthly_usage == 25.0
            
            # Check job cost
            job = Job.query.get(job.id)
            assert job.cost == 25.0
    
    def test_get_billing_summary(self, client, sample_org):
        """Test billing summary generation"""
        with app.app_context():
            # Add some usage
            today = date.today()
            daily_budget = BudgetService.get_or_create_budget(
                sample_org.id, 'daily', today
            )
            daily_budget.amount_used = 60.0
            
            monthly_date = today.replace(day=1)
            monthly_budget = BudgetService.get_or_create_budget(
                sample_org.id, 'monthly', monthly_date
            )
            monthly_budget.amount_used = 1500.0
            
            # Create some jobs
            for i in range(5):
                job = Job(
                    organization_id=sample_org.id,
                    name=f"Job {i}",
                    status="completed"
                )
                db.session.add(job)
            
            db.session.commit()
            
            # Get summary
            summary = BudgetService.get_billing_summary(sample_org.id)
            
            assert summary is not None
            assert summary['organization']['id'] == sample_org.id
            assert summary['daily']['usage'] == 60.0
            assert summary['daily']['limit'] == 100.0
            assert summary['monthly']['usage'] == 1500.0
            assert summary['monthly']['limit'] == 3000.0
            assert summary['jobs']['total'] == 5
            assert summary['jobs']['completed'] == 5


class TestAPI:
    """Test API endpoints"""
    
    def test_create_organization(self, client):
        """Test organization creation endpoint"""
        response = client.post('/api/organizations', json={
            'name': 'New Org',
            'daily_budget_limit': 200.0,
            'monthly_budget_limit': 6000.0,
            'budget_mode': 'hard'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['name'] == 'New Org'
        assert data['daily_budget_limit'] == 200.0
        assert data['budget_mode'] == 'hard'
    
    def test_list_organizations(self, client, sample_org):
        """Test organization listing endpoint"""
        with app.app_context():
            response = client.get('/api/organizations')
            
            assert response.status_code == 200
            data = response.get_json()
            assert len(data) >= 1
            assert any(org['id'] == sample_org.id for org in data)
    
    def test_create_job_within_budget(self, client, sample_org):
        """Test job creation within budget"""
        with app.app_context():
            response = client.post('/api/jobs', json={
                'organization_id': sample_org.id,
                'name': 'Test Job',
                'estimated_cost': 50.0
            })
            
            assert response.status_code == 201
            data = response.get_json()
            assert data['job']['status'] == 'pending'
            assert data['budget_check']['can_run'] is True
    
    def test_create_job_exceeding_budget_hard_mode(self, client, sample_org):
        """Test job creation exceeding budget in hard mode"""
        with app.app_context():
            # Switch to hard mode
            sample_org.budget_mode = 'hard'
            db.session.commit()
            
            response = client.post('/api/jobs', json={
                'organization_id': sample_org.id,
                'name': 'Expensive Job',
                'estimated_cost': 150.0
            })
            
            assert response.status_code == 201
            data = response.get_json()
            assert data['job']['status'] == 'budget_exceeded'
            assert data['budget_check']['can_run'] is False
    
    def test_complete_job(self, client, sample_org):
        """Test job completion endpoint"""
        with app.app_context():
            # Create a job
            job = Job(
                organization_id=sample_org.id,
                name="Test Job",
                status="running"
            )
            db.session.add(job)
            db.session.commit()
            job_id = job.id
            
            # Complete the job
            response = client.post(f'/api/jobs/{job_id}/complete', json={
                'cost': 30.0,
                'success': True
            })
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'completed'
            assert data['cost'] == 30.0
            
            # Verify budget was updated
            daily_usage = BudgetService.get_current_usage(sample_org.id, 'daily')
            assert daily_usage == 30.0
    
    def test_billing_summary_api(self, client, sample_org):
        """Test billing summary API endpoint"""
        with app.app_context():
            response = client.get(f'/api/billing/summary/{sample_org.id}')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['organization']['id'] == sample_org.id
            assert 'daily' in data
            assert 'monthly' in data
            assert 'jobs' in data
    
    def test_billing_summary_page(self, client):
        """Test billing summary page"""
        response = client.get('/billing/summary')
        assert response.status_code == 200
        assert b'Billing Summary' in response.data
    
    def test_dashboard_page(self, client):
        """Test dashboard page"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Budget Dashboard' in response.data or b'Aurea Orchestrator' in response.data
