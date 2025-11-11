# Aurea Orchestrator

**Automated Unified Reasoning & Execution Agents** with comprehensive telemetry and monitoring capabilities.

## Overview

Aurea Orchestrator is a FastAPI-based microservice designed to orchestrate LLM (Large Language Model) tasks with built-in telemetry, monitoring, and observability using OpenTelemetry, Prometheus, and Grafana.

## Features

- 🚀 **FastAPI-based REST API** for task orchestration
- 📊 **OpenTelemetry Integration** for distributed tracing and metrics
- 📈 **Prometheus Metrics** for monitoring and alerting
- 📉 **Grafana Dashboard** for visualization
- 🔍 **Request Latency Tracking** (p50, p95 percentiles)
- 💰 **LLM Cost Tracking** per model and task
- 🎯 **Token Usage Monitoring** across different LLM models
- 🐳 **Docker Compose** setup for easy deployment

## Architecture

```
┌─────────────────┐
│   Aurea         │
│   Orchestrator  │──────┐
│   (FastAPI)     │      │
└────────┬────────┘      │
         │               │
         │ /metrics      │ scrape
         │               │
         ▼               ▼
    ┌─────────────────────────┐
    │     Prometheus          │
    │   (Metrics Storage)     │
    └──────────┬──────────────┘
               │
               │ query
               ▼
        ┌──────────────┐
        │   Grafana    │
        │ (Dashboard)  │
        └──────────────┘
```

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Port 8000 (Orchestrator), 9090 (Prometheus), and 3000 (Grafana) available

### Running the Stack

1. **Clone the repository:**
   ```bash
   git clone https://github.com/andres20980/aurea-orchestrator.git
   cd aurea-orchestrator
   ```

2. **Start all services:**
   ```bash
   docker-compose up -d
   ```

3. **Verify services are running:**
   ```bash
   docker-compose ps
   ```

### Accessing the Services

- **Aurea Orchestrator API**: http://localhost:8000
- **API Documentation (Swagger)**: http://localhost:8000/docs
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000
  - Default credentials: `admin` / `admin`

## API Endpoints

### Core Endpoints

#### `GET /`
Health check and service information.

**Response:**
```json
{
  "service": "Aurea Orchestrator",
  "version": "1.0.0",
  "status": "running",
  "features": ["telemetry", "monitoring", "opentelemetry", "prometheus"]
}
```

#### `POST /tasks`
Create and execute a new task.

**Request Body:**
```json
{
  "id": "task-001",
  "description": "Analyze sentiment of customer feedback",
  "llm_model": "gpt-4",
  "max_tokens": 1000
}
```

**Response:**
```json
{
  "task_id": "task-001",
  "status": "completed",
  "result": "Task 'Analyze sentiment of customer feedback' processed successfully using gpt-4",
  "tokens_used": 856,
  "cost_usd": 0.02568,
  "latency_ms": 1523.45
}
```

#### `GET /tasks/{task_id}`
Retrieve task result by ID.

#### `GET /tasks`
List all processed tasks.

### Monitoring Endpoints

#### `GET /metrics`
Prometheus metrics endpoint in exposition format.

**Available Metrics:**
- `aurea_http_requests_total` - Total HTTP requests by method, endpoint, and status
- `aurea_request_latency_seconds` - Request latency histogram
- `aurea_tasks_total` - Total tasks processed by model and status
- `aurea_llm_tokens_total` - Total LLM tokens used by model
- `aurea_llm_cost_usd_total` - Total LLM cost in USD by model
- `aurea_active_tasks` - Current number of active tasks

#### `GET /metrics/summary`
Human-readable metrics summary.

**Response:**
```json
{
  "total_requests": 0,
  "total_tasks_processed": 42,
  "total_tokens_used": 35420,
  "total_cost_usd": 1.0626,
  "avg_latency_ms": 1845.32
}
```

## Supported LLM Models

The orchestrator supports multiple LLM models with different pricing:

| Model | Cost per 1K tokens |
|-------|-------------------|
| `gpt-4` | $0.03 |
| `gpt-3.5-turbo` | $0.002 |
| `claude-2` | $0.025 |
| `llama-2` | $0.001 |

## Grafana Dashboard

The pre-configured Grafana dashboard includes:

1. **Request Latency (p50 & p95)** - Track API response times
2. **Total LLM Tokens Used** - Cumulative token consumption
3. **Total LLM Cost** - Running cost of LLM operations
4. **LLM Token Usage Rate by Model** - Real-time token consumption
5. **Cost per Minute by Model** - Cost analysis over time
6. **Task Processing Rate** - Tasks processed per second
7. **Active Tasks** - Current concurrent task count
8. **HTTP Request Rate** - Request throughput

### Accessing the Dashboard

1. Navigate to http://localhost:3000
2. Login with `admin` / `admin`
3. Go to Dashboards → Aurea Orchestrator - Telemetry Dashboard

## Development

### Local Development (without Docker)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python main.py
   # or
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Access the API:**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - Metrics: http://localhost:8000/metrics

### Example Usage

```bash
# Create a task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "id": "task-001",
    "description": "Summarize this document",
    "llm_model": "gpt-4",
    "max_tokens": 500
  }'

# Get task result
curl http://localhost:8000/tasks/task-001

# View metrics summary
curl http://localhost:8000/metrics/summary

# View Prometheus metrics
curl http://localhost:8000/metrics
```

### Testing the Integration

```bash
# Generate some load
for i in {1..10}; do
  curl -X POST http://localhost:8000/tasks \
    -H "Content-Type: application/json" \
    -d "{
      \"id\": \"task-$i\",
      \"description\": \"Test task $i\",
      \"llm_model\": \"gpt-4\",
      \"max_tokens\": 1000
    }"
  sleep 1
done

# Check metrics
curl http://localhost:8000/metrics/summary
```

## Monitoring Setup

### Prometheus Configuration

The Prometheus configuration (`prometheus.yml`) is set up to:
- Scrape metrics from the orchestrator every 5 seconds
- Store metrics with proper labels
- Enable querying through the Prometheus UI

### Grafana Configuration

Grafana is pre-configured with:
- Prometheus as the default data source
- Auto-provisioned dashboard
- 5-second refresh rate for real-time monitoring

## Architecture Details

### Metrics Collection Flow

1. **Application Metrics**: FastAPI app emits metrics using `prometheus_client`
2. **OpenTelemetry**: Provides additional instrumentation and context
3. **Prometheus Scraping**: Prometheus pulls metrics from `/metrics` endpoint
4. **Grafana Visualization**: Queries Prometheus and displays dashboards

### Key Components

- **main.py**: Core application with FastAPI endpoints and metrics instrumentation
- **Dockerfile**: Container image for the orchestrator
- **docker-compose.yml**: Multi-service orchestration
- **prometheus.yml**: Prometheus scrape configuration
- **grafana/**: Grafana provisioning and dashboard definitions

## Stopping the Stack

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clears all data)
docker-compose down -v
```

## Troubleshooting

### Port Conflicts

If you encounter port conflicts, modify the port mappings in `docker-compose.yml`:

```yaml
services:
  orchestrator:
    ports:
      - "8001:8000"  # Change host port
```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f orchestrator
docker-compose logs -f prometheus
docker-compose logs -f grafana
```

### Grafana Dashboard Not Loading

1. Verify Prometheus data source is configured correctly
2. Check that Prometheus is scraping metrics: http://localhost:9090/targets
3. Ensure the orchestrator is running and accessible

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions, please open an issue on GitHub.
