"""
REST API for Aurea Orchestrator
Provides HTTP endpoints for agent version management and job metadata
"""

from flask import Flask, jsonify, request
from agents.versions import get_agent_version, get_all_agent_versions, compare_versions
from job_metadata import JobMetadataStore

app = Flask(__name__)
store = JobMetadataStore()


@app.route('/agents/versions', methods=['GET'])
def agents_versions():
    """
    Get all agent versions.
    
    Returns:
        JSON object with all agent versions
    """
    versions = get_all_agent_versions()
    return jsonify(versions)


@app.route('/agents/<agent_name>/version', methods=['GET'])
def agent_version(agent_name):
    """
    Get version for a specific agent.
    
    Args:
        agent_name: Name of the agent
        
    Returns:
        JSON object with agent version
    """
    try:
        version = get_agent_version(agent_name)
        return jsonify({
            'agent': agent_name,
            'version': version
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 404


@app.route('/versions/compare', methods=['POST'])
def versions_compare():
    """
    Compare two semantic versions.
    
    Request body:
        {
            "version1": "1.0.0",
            "version2": "1.1.0"
        }
        
    Returns:
        JSON object with comparison result
    """
    data = request.get_json()
    
    if not data or 'version1' not in data or 'version2' not in data:
        return jsonify({'error': 'version1 and version2 are required'}), 400
    
    result = compare_versions(data['version1'], data['version2'])
    
    description = 'equal' if result == 0 else ('less than' if result == -1 else 'greater than')
    
    return jsonify({
        'version1': data['version1'],
        'version2': data['version2'],
        'result': result,
        'description': description
    })


@app.route('/jobs', methods=['GET'])
def list_jobs():
    """
    List all jobs.
    
    Returns:
        JSON array of job IDs
    """
    jobs = store.list_jobs()
    return jsonify({'jobs': jobs})


@app.route('/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    """
    Get job metadata.
    
    Args:
        job_id: ID of the job
        
    Returns:
        JSON object with job metadata
    """
    metadata = store.load(job_id)
    
    if metadata is None:
        return jsonify({'error': f'Job {job_id} not found'}), 404
    
    return jsonify(metadata.to_dict())


@app.route('/jobs/compare', methods=['POST'])
def compare_jobs():
    """
    Compare two job runs.
    
    Request body:
        {
            "job1": "job_id_1",
            "job2": "job_id_2"
        }
        
    Returns:
        JSON object with comparison results
    """
    data = request.get_json()
    
    if not data or 'job1' not in data or 'job2' not in data:
        return jsonify({'error': 'job1 and job2 are required'}), 400
    
    comparison = store.compare_runs(data['job1'], data['job2'])
    
    if 'error' in comparison:
        return jsonify(comparison), 404
    
    return jsonify(comparison)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
