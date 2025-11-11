# Quick Start Guide

This guide will help you get the Aurea Orchestrator up and running in minutes.

## Method 1: Local Development (Fastest)

### Prerequisites
- Python 3.8 or higher
- pip

### Steps

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Start the server:**
```bash
python app.py
```

3. **Verify it's running:**
```bash
curl http://localhost:5000/health
```

4. **Run your first benchmark:**
```bash
curl -X POST http://localhost:5000/benchmark/run \
  -H "Content-Type: application/json" \
  -d '{"num_jobs": 10, "job_duration_ms": 100}'
```

## Method 2: Docker (Recommended for Production)

### Prerequisites
- Docker
- Docker Compose

### Steps

1. **Start the complete stack (App + Prometheus + Grafana):**
```bash
docker-compose up -d
```

2. **Access the services:**
- API: http://localhost:5000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

3. **Run a benchmark:**
```bash
curl -X POST http://localhost:5000/benchmark/run \
  -H "Content-Type: application/json" \
  -d '{"num_jobs": 50, "job_duration_ms": 100}'
```

4. **View metrics in Prometheus:**
- Open http://localhost:9090
- Query: `benchmark_throughput_jobs_per_second`

5. **Visualize in Grafana:**
- Open http://localhost:3000
- Login: admin/admin
- Add Prometheus data source: http://prometheus:9090
- Create dashboard using the queries from GRAFANA.md

## Method 3: Using Example Scripts

### Python Example

```bash
# Install example dependencies
pip install -r examples/requirements.txt

# Start the server (in one terminal)
python app.py

# Run the example (in another terminal)
python examples/benchmark_example.py
```

### Bash Example

```bash
# Start the server (in one terminal)
python app.py

# Run the example (in another terminal)
./examples/run_benchmarks.sh
```

## Common Use Cases

### 1. Quick Performance Test
```bash
curl -X POST http://localhost:5000/benchmark/run \
  -H "Content-Type: application/json" \
  -d '{"num_jobs": 10, "job_duration_ms": 50}'
```

### 2. Stress Test
```bash
curl -X POST http://localhost:5000/benchmark/run \
  -H "Content-Type: application/json" \
  -d '{"num_jobs": 1000, "job_duration_ms": 100}'
```

### 3. View Current Metrics
```bash
curl http://localhost:5000/metrics | grep "^benchmark"
```

## Understanding the Output

A typical benchmark response looks like this:

```json
{
  "benchmark_id": "benchmark-1699699800000",
  "num_jobs": 100,
  "completed_jobs": 100,
  "throughput": 250.5,          // Jobs per second
  "mean_latency": 0.399,        // Average time per job (seconds)
  "total_cost": 0.0399,         // Total cost in dollars
  "duration": 0.40,             // Total benchmark duration (seconds)
  "start_time": "2025-11-11T09:30:00.000Z",
  "end_time": "2025-11-11T09:30:00.400Z",
  "jobs": [...]                 // Individual job results
}
```

**Key Metrics:**
- **Throughput**: How many jobs completed per second (higher is better)
- **Mean Latency**: Average time to complete one job (lower is better)
- **Total Cost**: Calculated at $0.001 per second of execution

## Troubleshooting

### Server won't start
- Check if port 5000 is already in use: `lsof -i :5000`
- Kill existing process: `pkill -f "python app.py"`

### Tests failing
- Ensure dependencies are installed: `pip install -r requirements.txt requirements-dev.txt`
- Run tests: `pytest test_app.py -v`

### Docker Compose issues
- Check logs: `docker-compose logs -f`
- Restart services: `docker-compose restart`
- Rebuild: `docker-compose up -d --build`

### Prometheus not scraping metrics
- Verify app is running: `curl http://localhost:5000/metrics`
- Check Prometheus targets: http://localhost:9090/targets
- Review prometheus.yml configuration

## Next Steps

- Read [GRAFANA.md](GRAFANA.md) for detailed Grafana dashboard setup
- Review [README.md](README.md) for complete API documentation
- Run the test suite to understand all features: `pytest test_app.py -v`
- Try the example scripts in the `examples/` directory

## Getting Help

If you encounter issues:
1. Check the application logs
2. Verify all dependencies are installed
3. Ensure required ports (5000, 9090, 3000) are not in use
4. Review the test suite for usage examples
