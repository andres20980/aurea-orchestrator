# Quick Start Guide

This guide will help you get Aurea Orchestrator up and running in minutes.

## Prerequisites

- Docker and Docker Compose installed
- Ports 8000, 9090, and 3000 available

## Step 1: Start the Services

```bash
# Clone the repository
git clone https://github.com/andres20980/aurea-orchestrator.git
cd aurea-orchestrator

# Start all services (orchestrator, Prometheus, Grafana)
docker compose up -d
```

Wait about 30 seconds for all services to start.

## Step 2: Verify Services

Check that all services are running:

```bash
docker compose ps
```

You should see three services running:
- `aurea-orchestrator` (port 8000)
- `aurea-prometheus` (port 9090)
- `aurea-grafana` (port 3000)

## Step 3: Test the API

### Using curl:

```bash
# Create a task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "id": "my-first-task",
    "description": "Analyze customer feedback",
    "llm_model": "gpt-4",
    "max_tokens": 1000
  }'
```

### Using the test script:

```bash
chmod +x test.sh
./test.sh
```

### Using the Python example:

```bash
pip install requests
python example_usage.py
```

## Step 4: View Metrics and Dashboard

### API Documentation
Open http://localhost:8000/docs in your browser to see the interactive API documentation.

### Prometheus Metrics
1. Open http://localhost:9090
2. Try queries like:
   - `aurea_tasks_total` - Total tasks processed
   - `rate(aurea_llm_tokens_total[5m])` - Token usage rate
   - `aurea_llm_cost_usd_total` - Total cost

### Grafana Dashboard
1. Open http://localhost:3000
2. Login with username: `admin`, password: `admin`
3. Navigate to: Dashboards → Aurea Orchestrator - Telemetry Dashboard
4. Watch real-time metrics as you create tasks

## Step 5: Generate Some Load

Generate sample traffic to see metrics in action:

```bash
for i in {1..20}; do
  curl -X POST http://localhost:8000/tasks \
    -H "Content-Type: application/json" \
    -d "{\"id\": \"task-$i\", \"description\": \"Test task $i\", \"llm_model\": \"gpt-4\", \"max_tokens\": 500}"
  sleep 1
done
```

Watch the Grafana dashboard update in real-time!

## Common Commands

```bash
# View logs
docker compose logs -f orchestrator

# Stop all services
docker compose down

# Restart services
docker compose restart

# Stop and remove all data
docker compose down -v
```

## API Endpoints Quick Reference

- `GET /` - Service info
- `GET /health` - Health check
- `POST /tasks` - Create a task
- `GET /tasks/{task_id}` - Get task result
- `GET /tasks` - List all tasks
- `GET /metrics/summary` - Human-readable metrics
- `GET /metrics` - Prometheus metrics

## Troubleshooting

**Services won't start:**
- Check if ports 8000, 9090, 3000 are available
- Run `docker compose logs` to see error messages

**Grafana dashboard is empty:**
- Wait a few minutes for data to accumulate
- Create some tasks using the API
- Verify Prometheus is scraping: http://localhost:9090/targets

**Can't connect to API:**
- Verify the orchestrator is running: `docker compose ps`
- Check logs: `docker compose logs orchestrator`

## Next Steps

- Customize the dashboard in Grafana
- Modify `prometheus.yml` to adjust scrape intervals
- Extend `main.py` to add more LLM models
- Add alerting rules in Prometheus

For more information, see the main [README.md](README.md).
