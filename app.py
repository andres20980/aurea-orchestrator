"""
Aurea Orchestrator - Main Application
Flask app with budget management
"""
import os
from datetime import datetime, timezone
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
from models import db, Organization, Job
from budget_service import BudgetService

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///aurea.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)


@app.route('/')
def index():
    """Main dashboard"""
    return render_template('dashboard.html')


@app.route('/api/organizations', methods=['GET', 'POST'])
def organizations():
    """List or create organizations"""
    if request.method == 'POST':
        data = request.get_json()
        
        org = Organization(
            name=data['name'],
            daily_budget_limit=data.get('daily_budget_limit'),
            monthly_budget_limit=data.get('monthly_budget_limit'),
            budget_mode=data.get('budget_mode', BudgetService.get_default_mode())
        )
        
        db.session.add(org)
        db.session.commit()
        
        return jsonify(org.to_dict()), 201
    
    # GET
    orgs = Organization.query.all()
    return jsonify([org.to_dict() for org in orgs])


@app.route('/api/organizations/<int:org_id>', methods=['GET', 'PUT', 'DELETE'])
def organization_detail(org_id):
    """Get, update or delete an organization"""
    org = Organization.query.get_or_404(org_id)
    
    if request.method == 'DELETE':
        db.session.delete(org)
        db.session.commit()
        return '', 204
    
    if request.method == 'PUT':
        data = request.get_json()
        
        if 'name' in data:
            org.name = data['name']
        if 'daily_budget_limit' in data:
            org.daily_budget_limit = data['daily_budget_limit']
        if 'monthly_budget_limit' in data:
            org.monthly_budget_limit = data['monthly_budget_limit']
        if 'budget_mode' in data:
            org.budget_mode = data['budget_mode']
        
        db.session.commit()
        return jsonify(org.to_dict())
    
    # GET
    return jsonify(org.to_dict())


@app.route('/api/jobs', methods=['GET', 'POST'])
def jobs():
    """List or create jobs"""
    if request.method == 'POST':
        data = request.get_json()
        org_id = data['organization_id']
        estimated_cost = data.get('estimated_cost', 0.0)
        
        # Check budget before creating job
        can_run, reason, daily_usage, monthly_usage = BudgetService.check_budget(org_id, estimated_cost)
        
        job = Job(
            organization_id=org_id,
            name=data['name'],
            status='pending'
        )
        
        if not can_run:
            job.status = 'budget_exceeded'
        
        db.session.add(job)
        db.session.commit()
        
        return jsonify({
            'job': job.to_dict(),
            'budget_check': {
                'can_run': can_run,
                'reason': reason,
                'daily_usage': daily_usage,
                'monthly_usage': monthly_usage
            }
        }), 201
    
    # GET
    org_id = request.args.get('organization_id', type=int)
    if org_id:
        jobs_list = Job.query.filter_by(organization_id=org_id).all()
    else:
        jobs_list = Job.query.all()
    
    return jsonify([job.to_dict() for job in jobs_list])


@app.route('/api/jobs/<int:job_id>/start', methods=['POST'])
def start_job(job_id):
    """Start a job"""
    job = Job.query.get_or_404(job_id)
    
    if job.status != 'pending':
        return jsonify({'error': 'Job is not in pending state'}), 400
    
    # Re-check budget
    estimated_cost = request.get_json().get('estimated_cost', 0.0)
    can_run, reason, _, _ = BudgetService.check_budget(job.organization_id, estimated_cost)
    
    if not can_run:
        job.status = 'budget_exceeded'
        db.session.commit()
        return jsonify({
            'error': reason,
            'job': job.to_dict()
        }), 403
    
    job.status = 'running'
    job.started_at = datetime.now(timezone.utc)
    db.session.commit()
    
    return jsonify(job.to_dict())


@app.route('/api/jobs/<int:job_id>/complete', methods=['POST'])
def complete_job(job_id):
    """Complete a job and record its cost"""
    job = Job.query.get_or_404(job_id)
    data = request.get_json()
    
    cost = data.get('cost', 0.0)
    success = data.get('success', True)
    
    job.status = 'completed' if success else 'failed'
    job.completed_at = datetime.now(timezone.utc)
    
    # Record cost to budget
    BudgetService.record_job_cost(job.organization_id, job_id, cost)
    
    return jsonify(job.to_dict())


@app.route('/billing/summary')
def billing_summary_page():
    """Billing summary page"""
    org_id = request.args.get('organization_id', type=int)
    
    if not org_id:
        orgs = Organization.query.all()
        return render_template('billing_summary.html', organizations=orgs)
    
    summary = BudgetService.get_billing_summary(org_id)
    if not summary:
        return "Organization not found", 404
    
    return render_template('billing_summary.html', summary=summary, organizations=[])


@app.route('/api/billing/summary/<int:org_id>')
def billing_summary_api(org_id):
    """API endpoint for billing summary"""
    summary = BudgetService.get_billing_summary(org_id)
    
    if not summary:
        return jsonify({'error': 'Organization not found'}), 404
    
    return jsonify(summary)


@app.cli.command()
def init_db():
    """Initialize the database"""
    db.create_all()
    print("Database initialized!")


@app.cli.command()
def seed_data():
    """Seed the database with sample data"""
    # Create a sample organization
    org = Organization(
        name="Sample Organization",
        daily_budget_limit=500.0,
        monthly_budget_limit=15000.0,
        budget_mode='soft'
    )
    db.session.add(org)
    db.session.commit()
    
    print(f"Created organization: {org.name} (ID: {org.id})")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
