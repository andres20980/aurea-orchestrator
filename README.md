# Aurea Orchestrator - Monitoring & Metrics

Automated Unified Reasoning & Execution Agents with monitoring for cost and latency tracking.

## Features

- **Task Monitoring Middleware**: Automatically log task execution metrics
- **Metrics Storage**: PostgreSQL database for storing task metrics
- **REST API**: Query aggregated statistics per job
- **Grafana Integration**: Pre-configured dashboards for visualization

## Architecture

The monitoring system tracks the following metrics for each task:
- Task name
- Model used
- Token count
- Latency (ms)
- Cost estimate

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Grafana 8.0+ (optional, for visualization)

### Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Configure database connection:
```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/aurea_orchestrator"
```

Or create a `.env` file:
```
DATABASE_URL=postgresql://user:password@localhost:5432/aurea_orchestrator
PORT=4000
```

3. Initialize the database:
```bash
python -c "from models import init_db; init_db()"
```

4. Run the application:
```bash
python app.py
```

The server will start on `http://localhost:4000`

## Usage

### Monitoring Tasks

Use the `@monitor_task` decorator to automatically track task execution:

```python
from middleware import monitor_task

@monitor_task(
    job_id="job_123",
    task_name="text_generation",
    model_used="gpt-4"
)
def generate_text(prompt):
    # Your task implementation
    result = call_model(prompt)
    token_count = count_tokens(result)
    
    # Return result and token count
    return result, token_count

# Or return a dict with 'tokens' key
@monitor_task(
    job_id="job_456",
    task_name="summarization",
    model_used="claude-3-sonnet"
)
def summarize_text(text):
    result = call_model(text)
    return {
        'summary': result,
        'tokens': count_tokens(result)
    }
```

### Custom Cost Estimation

Provide your own cost estimation function:

```python
from middleware import monitor_task

def my_cost_estimator(model_name, token_count):
    # Your custom pricing logic
    if model_name == "custom-model":
        return token_count * 0.00005
    return token_count * 0.00001

@monitor_task(
    job_id="job_789",
    task_name="custom_task",
    model_used="custom-model",
    estimate_cost_fn=my_cost_estimator
)
def custom_task(input_data):
    # Task implementation
    return result, tokens
```

### API Endpoints

#### Get Job Metrics

```bash
GET /metrics/jobs/{job_id}
```

Returns aggregated statistics for a specific job:

```json
{
  "job_id": "job_123",
  "total_tasks": 10,
  "total_tokens": 5000,
  "total_latency_ms": 12500.5,
  "avg_latency_ms": 1250.05,
  "total_cost": 0.15,
  "avg_cost": 0.015,
  "task_breakdown": [
    {
      "task_name": "text_generation",
      "count": 5,
      "avg_latency_ms": 1200.0,
      "total_cost": 0.075
    },
    {
      "task_name": "summarization",
      "count": 5,
      "avg_latency_ms": 1300.1,
      "total_cost": 0.075
    }
  ],
  "model_usage": [
    {
      "model": "gpt-4",
      "count": 7,
      "total_tokens": 3500,
      "total_cost": 0.105
    },
    {
      "model": "claude-3-sonnet",
      "count": 3,
      "total_tokens": 1500,
      "total_cost": 0.045
    }
  ]
}
```

#### Get Job Details

```bash
GET /metrics/jobs/{job_id}/details?limit=100&offset=0
```

Returns individual metrics for a job with pagination.

#### List All Jobs

```bash
GET /metrics/jobs
```

Returns all jobs with basic statistics.

#### Create Metric Manually

```bash
POST /metrics
Content-Type: application/json

{
  "job_id": "job_123",
  "task_name": "text_generation",
  "model_used": "gpt-4",
  "token_count": 500,
  "latency_ms": 1250.5,
  "cost_estimate": 0.015
}
```

#### Health Check

```bash
GET /health
```

## Grafana Setup

### 1. Add PostgreSQL Data Source

In Grafana:
1. Go to Configuration → Data Sources
2. Add PostgreSQL data source
3. Configure connection:
   - Host: `localhost:5432`
   - Database: `aurea_orchestrator`
   - User: your database user
   - Password: your database password
   - SSL Mode: disable (or configure as needed)

### 2. Import Dashboard

1. Go to Dashboards → Import
2. Upload `grafana-dashboard.json`
3. Select your PostgreSQL data source

### 3. Dashboard Features

The pre-configured dashboard includes:

- **Total Cost by Job**: Time series graph showing cost trends
- **Average Latency by Task**: Performance monitoring per task type
- **Token Usage by Model**: Pie chart showing token distribution
- **Cost Breakdown by Model**: Cost allocation across models
- **Task Execution Timeline**: Recent task executions table
- **Total Metrics**: Overall statistics (tasks, tokens, cost)
- **Active Jobs**: Number of unique jobs
- **Latency Distribution**: Histogram of task latencies

## Database Schema

```sql
CREATE TABLE metrics (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(255) NOT NULL,
    task_name VARCHAR(255) NOT NULL,
    model_used VARCHAR(255) NOT NULL,
    token_count INTEGER NOT NULL,
    latency_ms FLOAT NOT NULL,
    cost_estimate FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_metrics_job_id ON metrics(job_id);
```

## Example: Complete Workflow

```python
from middleware import monitor_task

# Define your tasks with monitoring
@monitor_task("job_001", "data_processing", "gpt-4")
def process_data(data):
    # Process the data
    result = transform(data)
    tokens = len(result.split())
    return result, tokens

@monitor_task("job_001", "analysis", "claude-3-opus")
def analyze_results(data):
    # Analyze
    analysis = perform_analysis(data)
    return {'result': analysis, 'tokens': 1500}

# Execute tasks
data = load_data()
processed = process_data(data)
results = analyze_results(processed)

# Query metrics via API
import requests
response = requests.get('http://localhost:4000/metrics/jobs/job_001')
stats = response.json()
print(f"Total cost: ${stats['total_cost']:.4f}")
print(f"Average latency: {stats['avg_latency_ms']:.2f}ms")
```

## Testing

Run tests:
```bash
python -m pytest tests/
```

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string (required)
- `PORT`: Application port (default: 4000)

## Default Model Pricing

The system includes default pricing for common models (per 1000 tokens):

| Model | Price per 1K tokens |
|-------|-------------------|
| gpt-4 | $0.03 |
| gpt-4-turbo | $0.01 |
| gpt-3.5-turbo | $0.002 |
| claude-3-opus | $0.015 |
| claude-3-sonnet | $0.003 |
| claude-3-haiku | $0.00025 |
| llama-2-70b | $0.0007 |
| llama-2-13b | $0.0002 |

You can override these with custom cost estimation functions.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT
