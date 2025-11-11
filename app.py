"""
Flask application for aurea-orchestrator monitoring.
"""
from flask import Flask, jsonify, request
from models import init_db, get_job_stats, Metric, get_session
from middleware import MonitoringMiddleware, log_metric
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)

# Initialize monitoring middleware
monitoring = MonitoringMiddleware(app)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200


@app.route('/metrics/jobs/<job_id>', methods=['GET'])
def get_job_metrics(job_id):
    """
    Get aggregated metrics for a specific job.
    
    Args:
        job_id: Job identifier from URL path
        
    Returns:
        JSON with aggregated statistics including:
        - total_tasks: Total number of tasks
        - total_tokens: Total tokens processed
        - total_latency_ms: Total latency
        - avg_latency_ms: Average latency per task
        - total_cost: Total estimated cost
        - avg_cost: Average cost per task
        - task_breakdown: Breakdown by task name
        - model_usage: Breakdown by model
    """
    try:
        stats = get_job_stats(job_id)
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/metrics', methods=['POST'])
def create_metric():
    """
    Create a new metric entry.
    
    Expected JSON body:
    {
        "job_id": "string",
        "task_name": "string",
        "model_used": "string",
        "token_count": int,
        "latency_ms": float,
        "cost_estimate": float
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['job_id', 'task_name', 'model_used', 'token_count', 'latency_ms', 'cost_estimate']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Log the metric
        log_metric(
            job_id=data['job_id'],
            task_name=data['task_name'],
            model_used=data['model_used'],
            token_count=data['token_count'],
            latency_ms=data['latency_ms'],
            cost_estimate=data['cost_estimate']
        )
        
        return jsonify({'message': 'Metric created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/metrics/jobs/<job_id>/details', methods=['GET'])
def get_job_details(job_id):
    """
    Get detailed metrics for a specific job (all individual metrics).
    
    Args:
        job_id: Job identifier from URL path
        
    Query parameters:
        - limit: Maximum number of records (default: 100)
        - offset: Offset for pagination (default: 0)
    """
    try:
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        session = get_session()
        try:
            metrics = session.query(Metric).filter(
                Metric.job_id == job_id
            ).order_by(
                Metric.created_at.desc()
            ).limit(limit).offset(offset).all()
            
            return jsonify({
                'job_id': job_id,
                'count': len(metrics),
                'metrics': [m.to_dict() for m in metrics]
            }), 200
        finally:
            session.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/metrics/jobs', methods=['GET'])
def list_jobs():
    """
    List all jobs with metrics.
    
    Returns a list of unique job IDs with basic statistics.
    """
    try:
        from sqlalchemy import func
        session = get_session()
        try:
            jobs = session.query(
                Metric.job_id,
                func.count(Metric.id).label('task_count'),
                func.sum(Metric.cost_estimate).label('total_cost'),
                func.max(Metric.created_at).label('last_updated')
            ).group_by(Metric.job_id).all()
            
            return jsonify({
                'jobs': [
                    {
                        'job_id': j.job_id,
                        'task_count': j.task_count,
                        'total_cost': float(j.total_cost) if j.total_cost else 0.0,
                        'last_updated': j.last_updated.isoformat() if j.last_updated else None
                    } for j in jobs
                ]
            }), 200
        finally:
            session.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def create_app():
    """Application factory."""
    # Initialize database
    init_db()
    return app


if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Run the application
    port = int(os.getenv('PORT', 4000))
    app.run(host='0.0.0.0', port=port, debug=True)
