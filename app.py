"""
Aurea Orchestrator - API Server for synthetic workload benchmarking
"""
from flask import Flask, request, jsonify
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import time
import threading
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

app = Flask(__name__)

# Prometheus metrics
benchmark_runs = Counter('benchmark_runs_total', 'Total number of benchmark runs')
benchmark_jobs = Counter('benchmark_jobs_total', 'Total number of jobs executed')
benchmark_throughput = Gauge('benchmark_throughput_jobs_per_second', 'Current benchmark throughput')
benchmark_mean_latency = Gauge('benchmark_mean_latency_seconds', 'Current benchmark mean latency')
benchmark_cost = Gauge('benchmark_cost_total', 'Current benchmark cost')
job_duration_histogram = Histogram('benchmark_job_duration_seconds', 'Job execution duration')


def execute_synthetic_job(job_id, duration_ms=100):
    """
    Execute a synthetic workload job.
    
    Args:
        job_id: Unique identifier for the job
        duration_ms: Duration of the job in milliseconds
    
    Returns:
        dict: Job execution results including latency and cost
    """
    start_time = time.time()
    
    # Simulate work with some random variation (±20%)
    actual_duration = duration_ms * (1 + random.uniform(-0.2, 0.2)) / 1000
    time.sleep(actual_duration)
    
    end_time = time.time()
    latency = end_time - start_time
    
    # Simple cost calculation: $0.001 per second of execution
    cost = latency * 0.001
    
    # Record metrics
    job_duration_histogram.observe(latency)
    benchmark_jobs.inc()
    
    return {
        'job_id': job_id,
        'latency': latency,
        'cost': cost,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'aurea-orchestrator'}), 200


@app.route('/benchmark/run', methods=['POST'])
def run_benchmark():
    """
    Execute synthetic workload benchmark with N parallel jobs.
    
    Expected JSON payload:
    {
        "num_jobs": 100,           # Number of parallel jobs to execute
        "job_duration_ms": 100     # Duration of each job in milliseconds (optional, default: 100)
    }
    
    Returns:
    {
        "benchmark_id": "unique-id",
        "num_jobs": 100,
        "throughput": 50.5,        # jobs per second
        "mean_latency": 0.198,     # seconds
        "total_cost": 0.0198,      # dollars
        "start_time": "2025-11-11T09:30:00.000Z",
        "end_time": "2025-11-11T09:30:02.000Z",
        "duration": 2.0,           # seconds
        "jobs": [...]              # individual job results
    }
    """
    # Increment benchmark run counter
    benchmark_runs.inc()
    
    # Parse request
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON payload'}), 400
    
    num_jobs = data.get('num_jobs')
    if not num_jobs or not isinstance(num_jobs, int) or num_jobs < 1:
        return jsonify({'error': 'num_jobs must be a positive integer'}), 400
    
    job_duration_ms = data.get('job_duration_ms', 100)
    if not isinstance(job_duration_ms, (int, float)) or job_duration_ms < 0:
        return jsonify({'error': 'job_duration_ms must be a non-negative number'}), 400
    
    # Generate benchmark ID
    benchmark_id = f"benchmark-{int(time.time() * 1000)}"
    
    # Execute benchmark
    start_time = time.time()
    start_timestamp = datetime.now(timezone.utc).isoformat()
    
    job_results = []
    
    # Execute jobs in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=min(num_jobs, 50)) as executor:
        futures = [
            executor.submit(execute_synthetic_job, f"{benchmark_id}-job-{i}", job_duration_ms)
            for i in range(num_jobs)
        ]
        
        for future in as_completed(futures):
            try:
                result = future.result()
                job_results.append(result)
            except Exception as e:
                app.logger.error(f"Job execution failed: {e}")
    
    end_time = time.time()
    end_timestamp = datetime.now(timezone.utc).isoformat()
    
    # Calculate metrics
    total_duration = end_time - start_time
    throughput = num_jobs / total_duration if total_duration > 0 else 0
    
    latencies = [job['latency'] for job in job_results]
    mean_latency = sum(latencies) / len(latencies) if latencies else 0
    
    total_cost = sum(job['cost'] for job in job_results)
    
    # Update Prometheus metrics
    benchmark_throughput.set(throughput)
    benchmark_mean_latency.set(mean_latency)
    benchmark_cost.set(total_cost)
    
    # Build response
    response = {
        'benchmark_id': benchmark_id,
        'num_jobs': num_jobs,
        'completed_jobs': len(job_results),
        'throughput': round(throughput, 2),
        'mean_latency': round(mean_latency, 4),
        'total_cost': round(total_cost, 6),
        'start_time': start_timestamp,
        'end_time': end_timestamp,
        'duration': round(total_duration, 2),
        'jobs': job_results
    }
    
    return jsonify(response), 200


@app.route('/metrics', methods=['GET'])
def metrics():
    """
    Prometheus metrics endpoint for Grafana.
    
    Returns metrics in Prometheus format that can be scraped by Prometheus
    and visualized in Grafana.
    """
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
