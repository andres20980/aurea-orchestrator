# Aurea Orchestrator

Automated Unified Reasoning & Execution Agents with dynamic model routing.

## Features

The Aurea Orchestrator provides intelligent model routing based on:
- **Cost efficiency**: Optimizes for lowest cost per request
- **Quality**: Tracks success rates for each model
- **Latency**: Monitors average response time

The system dynamically adjusts selection weights based on performance variance across models.

## Installation

```bash
pip install -r requirements.txt
```

## Running the Server

```bash
uvicorn app.main:app --reload
```

The server will start on `http://localhost:8000`.

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### GET /
Root endpoint with service information.

### GET /router/select
Select the best model based on current metrics and weights.

**Response:**
```json
{
  "selected_model": "gpt-3.5-turbo",
  "score": 0.85,
  "weights": {
    "cost_weight": 0.33,
    "quality_weight": 0.34,
    "latency_weight": 0.33
  }
}
```

### POST /router/record
Record metrics for a model request.

**Request:**
```json
{
  "model": "gpt-4",
  "latency": 0.5,
  "cost": 0.02,
  "success": true
}
```

**Response:**
```json
{
  "status": "recorded",
  "model": "gpt-4"
}
```

### GET /router/metrics
Get metrics summary for all models.

**Response:**
```json
{
  "gpt-4": {
    "total_requests": 100,
    "success_rate": 0.98,
    "average_latency": 0.65,
    "average_cost": 0.025,
    "score": 0.82,
    "last_updated": "2025-11-11T08:53:00"
  },
  "gpt-3.5-turbo": {
    "total_requests": 150,
    "success_rate": 0.95,
    "average_latency": 0.35,
    "average_cost": 0.002,
    "score": 0.91,
    "last_updated": "2025-11-11T08:53:00"
  }
}
```

### POST /router/optimize
Optimize selection weights based on recent performance. **Should be called weekly**.

The optimization analyzes variance in metrics across models and adjusts weights to better differentiate between models.

**Response:**
```json
{
  "status": "optimized",
  "weights": {
    "cost_weight": 0.45,
    "quality_weight": 0.25,
    "latency_weight": 0.30
  },
  "metrics_summary": { ... }
}
```

### GET /router/weights
Get current selection weights.

**Response:**
```json
{
  "cost_weight": 0.33,
  "quality_weight": 0.34,
  "latency_weight": 0.33
}
```

### PUT /router/weights
Manually update selection weights.

**Request:**
```json
{
  "cost_weight": 0.5,
  "quality_weight": 0.3,
  "latency_weight": 0.2
}
```

Note: Weights must sum to 1.0.

## Usage Example

### 1. Start the server
```bash
uvicorn app.main:app --reload
```

### 2. Record some requests
```python
import requests

# Record successful GPT-4 request
requests.post("http://localhost:8000/router/record", json={
    "model": "gpt-4",
    "latency": 0.8,
    "cost": 0.03,
    "success": True
})

# Record successful GPT-3.5 request
requests.post("http://localhost:8000/router/record", json={
    "model": "gpt-3.5-turbo",
    "latency": 0.3,
    "cost": 0.002,
    "success": True
})
```

### 3. Get model recommendation
```python
response = requests.get("http://localhost:8000/router/select")
print(response.json())
# Output: {"selected_model": "gpt-3.5-turbo", "score": 0.85, ...}
```

### 4. View metrics
```python
response = requests.get("http://localhost:8000/router/metrics")
print(response.json())
```

### 5. Optimize weights (weekly task)
```python
response = requests.post("http://localhost:8000/router/optimize")
print(response.json())
```

## How It Works

### Dynamic Scoring

Each model receives a composite score based on:
1. **Cost Score**: Lower cost = higher score (inverted and normalized)
2. **Quality Score**: Success rate (0-1)
3. **Latency Score**: Lower latency = higher score (inverted and normalized)

The final score is a weighted average:
```
score = cost_score × cost_weight + quality_score × quality_weight + latency_score × latency_weight
```

### Weight Optimization

The `/router/optimize` endpoint analyzes variance in metrics across models:
- Metrics with higher variance are more useful for differentiation
- Weights are adjusted proportionally to variance
- Should be called weekly to adapt to changing patterns

### Persistence

Metrics and weights are persisted to JSON files:
- `metrics_data.json`: Historical metrics for each model
- `router_weights.json`: Current selection weights

## Testing

Run tests:
```bash
pytest tests/
```

Run tests with coverage:
```bash
pytest tests/ --cov=app --cov-report=html
```

## Available Models

- gpt-4
- gpt-3.5-turbo
- claude-3-opus
- claude-3-sonnet
- llama-2-70b

## Scheduled Tasks

Set up a weekly cron job to optimize weights:
```bash
# Add to crontab (runs every Sunday at 2 AM)
0 2 * * 0 curl -X POST http://localhost:8000/router/optimize
```

## Architecture

```
aurea-orchestrator/
├── app/
│   ├── __init__.py
│   ├── main.py         # FastAPI application and endpoints
│   └── router.py       # Model router with scoring logic
├── tests/
│   ├── __init__.py
│   ├── test_api.py     # API endpoint tests
│   └── test_router.py  # Router logic tests
├── requirements.txt
└── README.md
```

## License

MIT
