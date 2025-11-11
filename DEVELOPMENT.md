# Development Guide

Guide for developers working on the Aurea Orchestrator project.

## Development Setup

### Local Development (without Docker)

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   # Development mode with auto-reload
   uvicorn main:app --reload --host 127.0.0.1 --port 8000
   
   # Or use the Python script
   python main.py
   ```

4. **Access the application:**
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - Metrics: http://localhost:8000/metrics

### Docker Development

1. **Build the image:**
   ```bash
   docker compose build
   ```

2. **Run all services:**
   ```bash
   docker compose up
   ```

3. **Run in detached mode:**
   ```bash
   docker compose up -d
   ```

4. **View logs:**
   ```bash
   # All services
   docker compose logs -f
   
   # Specific service
   docker compose logs -f orchestrator
   ```

## Project Structure

```
aurea-orchestrator/
├── main.py                    # Main FastAPI application
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container image definition
├── docker-compose.yml         # Multi-service orchestration
├── prometheus.yml             # Prometheus configuration
├── .gitignore                # Git ignore rules
├── README.md                  # Main documentation
├── QUICKSTART.md             # Quick start guide
├── METRICS.md                # Metrics documentation
├── test.sh                   # Test script
├── example_usage.py          # Python usage example
└── grafana/
    ├── dashboards/
    │   └── aurea-orchestrator.json    # Pre-built dashboard
    └── provisioning/
        ├── dashboards/
        │   └── dashboards.yml         # Dashboard provisioning
        └── datasources/
            └── prometheus.yml         # Data source config
```

## Code Style

### Python Style Guide
- Follow PEP 8
- Use type hints where possible
- Document functions with docstrings
- Maximum line length: 100 characters

### Example:
```python
from typing import Optional

def calculate_cost(model: str, tokens: int) -> float:
    """
    Calculate LLM cost based on model and tokens.
    
    Args:
        model: LLM model name
        tokens: Number of tokens used
        
    Returns:
        Cost in USD
    """
    # Implementation
    pass
```

## Adding New Features

### Adding a New LLM Model

1. **Update cost table in `main.py`:**
   ```python
   cost_per_1k_tokens = {
       'gpt-4': 0.03,
       'gpt-3.5-turbo': 0.002,
       'claude-2': 0.025,
       'llama-2': 0.001,
       'new-model': 0.015,  # Add new model
   }
   ```

2. **Update documentation in README.md**

### Adding a New Endpoint

1. **Add endpoint in `main.py`:**
   ```python
   @app.get("/new-endpoint")
   async def new_endpoint():
       """Endpoint description"""
       # Implementation
       return {"status": "ok"}
   ```

2. **Add metrics if needed:**
   ```python
   new_metric = Counter('new_metric_total', 'Description')
   new_metric.inc()
   ```

3. **Update Swagger documentation** (automatic via FastAPI)

### Adding a New Metric

1. **Define metric in `main.py`:**
   ```python
   from prometheus_client import Counter, Histogram, Gauge
   
   my_metric = Counter(
       'aurea_my_metric_total',
       'Description of metric',
       ['label1', 'label2']
   )
   ```

2. **Use metric in code:**
   ```python
   my_metric.labels(label1='value', label2='value').inc()
   ```

3. **Add to Grafana dashboard:**
   - Edit dashboard JSON or use Grafana UI
   - Create new panel with PromQL query
   - Save and export dashboard

## Testing

### Manual Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test task creation
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"id": "test", "description": "Test", "llm_model": "gpt-4", "max_tokens": 100}'

# Test metrics
curl http://localhost:8000/metrics
```

### Using the Test Script

```bash
./test.sh
```

### Using Python Example

```bash
python example_usage.py
```

## Debugging

### Viewing Logs

**Application logs:**
```bash
# Docker
docker compose logs -f orchestrator

# Local
# Logs appear in console when running uvicorn
```

**Prometheus logs:**
```bash
docker compose logs -f prometheus
```

**Grafana logs:**
```bash
docker compose logs -f grafana
```

### Common Issues

**Port already in use:**
```bash
# Find what's using the port
lsof -i :8000

# Kill the process or use a different port
uvicorn main:app --port 8001
```

**Docker build fails:**
```bash
# Clean build
docker compose build --no-cache

# Check for errors
docker compose logs
```

**Metrics not appearing:**
- Check Prometheus targets: http://localhost:9090/targets
- Verify metrics endpoint: http://localhost:8000/metrics
- Check Prometheus config: prometheus.yml

## Environment Variables

The application supports these environment variables:

```bash
# Set in docker-compose.yml or .env file
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=info
```

## Performance Optimization

### Application Level
- Use async/await for I/O operations
- Add caching for frequently accessed data
- Implement connection pooling for external services

### Prometheus Level
- Reduce scrape interval if not needed
- Use recording rules for complex queries
- Set appropriate retention period

### Grafana Level
- Use query caching
- Limit time range for heavy queries
- Use template variables for filtering

## Contributing Guidelines

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/my-feature
   ```
3. **Make changes and test**
4. **Commit with clear messages**
   ```bash
   git commit -m "Add feature: description"
   ```
5. **Push and create pull request**
   ```bash
   git push origin feature/my-feature
   ```

## Release Process

1. Update version in `main.py`
2. Update CHANGELOG.md
3. Create git tag
4. Build and push Docker image
5. Update documentation

## Useful Commands

```bash
# Format code
black main.py

# Check types
mypy main.py

# Security check
bandit -r .

# Check dependencies
pip list --outdated

# Update dependencies
pip install --upgrade -r requirements.txt
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/naming/)
- [Grafana Tutorials](https://grafana.com/tutorials/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

## Getting Help

- Check existing issues on GitHub
- Read the documentation
- Ask questions in discussions
- Join the community chat
