# aurea-orchestrator
Automated Unified Reasoning & Execution Agents

A lightweight API service for executing synthetic workload benchmarks and exporting metrics to Grafana via Prometheus.

## Features

- **Synthetic Workload Benchmarking**: Execute N parallel jobs to simulate workload
- **Performance Metrics**: Track throughput (jobs/second), mean latency, and cost
- **Prometheus Integration**: Export metrics in Prometheus format for Grafana visualization
- **RESTful API**: Simple HTTP endpoints for benchmark execution and monitoring

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. Clone the repository:
```bash
git clone https://github.com/andres20980/aurea-orchestrator.git
cd aurea-orchestrator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### POST /benchmark/run

Execute a synthetic workload benchmark with N parallel jobs.

**Request Body:**
```json
{
  "num_jobs": 100,
  "job_duration_ms": 100
}
```

**Parameters:**
- `num_jobs` (required): Number of parallel jobs to execute (positive integer)
- `job_duration_ms` (optional): Duration of each job in milliseconds (default: 100)

**Response:**
```json
{
  "benchmark_id": "benchmark-1699699800000",
  "num_jobs": 100,
  "completed_jobs": 100,
  "throughput": 50.5,
  "mean_latency": 0.198,
  "total_cost": 0.0198,
  "start_time": "2025-11-11T09:30:00.000Z",
  "end_time": "2025-11-11T09:30:02.000Z",
  "duration": 2.0,
  "jobs": [
    {
      "job_id": "benchmark-1699699800000-job-0",
      "latency": 0.201,
      "cost": 0.000201,
      "timestamp": "2025-11-11T09:30:00.100Z"
    }
  ]
}
```

**Metrics Explanation:**
- `throughput`: Jobs completed per second
- `mean_latency`: Average job execution time in seconds
- `total_cost`: Total cost in dollars (calculated as $0.001 per second of execution)

**Example:**
```bash
curl -X POST http://localhost:5000/benchmark/run \
  -H "Content-Type: application/json" \
  -d '{"num_jobs": 50, "job_duration_ms": 100}'
```

### GET /metrics

Prometheus metrics endpoint for Grafana integration.

**Response:** Prometheus text format

**Metrics Exposed:**
- `benchmark_runs_total`: Total number of benchmark runs
- `benchmark_jobs_total`: Total number of jobs executed
- `benchmark_throughput_jobs_per_second`: Current benchmark throughput
- `benchmark_mean_latency_seconds`: Current benchmark mean latency
- `benchmark_cost_total`: Current benchmark cost
- `benchmark_job_duration_seconds`: Histogram of job execution durations

**Example:**
```bash
curl http://localhost:5000/metrics
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "aurea-orchestrator"
}
```

## Grafana Integration

### Setup with Prometheus

1. Configure Prometheus to scrape the metrics endpoint by adding this to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'aurea-orchestrator'
    static_configs:
      - targets: ['localhost:5000']
    metrics_path: '/metrics'
    scrape_interval: 5s
```

2. In Grafana, add Prometheus as a data source
3. Create dashboards using the exposed metrics

### Example Grafana Queries

**Throughput Over Time:**
```promql
benchmark_throughput_jobs_per_second
```

**Mean Latency Over Time:**
```promql
benchmark_mean_latency_seconds
```

**Total Jobs Executed:**
```promql
benchmark_jobs_total
```

**Job Duration Percentiles:**
```promql
histogram_quantile(0.95, benchmark_job_duration_seconds_bucket)
```

## Development

### Running Tests

Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

Run tests:
```bash
pytest test_app.py -v
```

### Project Structure

```
aurea-orchestrator/
├── app.py                  # Main Flask application
├── test_app.py            # Test suite
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Development dependencies
├── .gitignore            # Git ignore patterns
└── README.md             # This file
```

## License

MIT
