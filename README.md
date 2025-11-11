# aurea-orchestrator
Automated Unified Reasoning & Execution Agents

A FastAPI-based orchestrator with intelligent caching for LLM and embedding operations using Redis.

## Features

- **Redis Caching**: Intelligent caching system for LLM responses and embeddings
- **Cache Decorators**: Easy-to-use decorators for caching function results
- **Cache Management**: Protected endpoints for viewing stats and clearing cache
- **Prometheus Metrics**: Built-in metrics for cache hits, misses, and hit rates
- **Configurable TTL**: Separate TTL configurations for LLM and embedding caches
- **Cache Bypass**: Optional cache bypass for real-time requests

## Installation

### Option 1: Docker Compose (Recommended)

The easiest way to get started is using Docker Compose, which sets up both the application and Redis:

```bash
# Clone the repository
git clone https://github.com/andres20980/aurea-orchestrator.git
cd aurea-orchestrator

# Start the services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the services
docker-compose down
```

The application will be available at `http://localhost:8000`.

### Option 2: Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/andres20980/aurea-orchestrator.git
cd aurea-orchestrator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

3. Set up Redis:
```bash
# Using Docker
docker run -d -p 6379:6379 redis:latest

# Or install Redis locally
# Ubuntu/Debian: sudo apt-get install redis-server
# macOS: brew install redis
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Configuration

The application is configured via environment variables (see `.env.example`):

### Redis Settings
- `REDIS_HOST`: Redis server host (default: `localhost`)
- `REDIS_PORT`: Redis server port (default: `6379`)
- `REDIS_DB`: Redis database number (default: `0`)
- `REDIS_PASSWORD`: Redis password (optional)
- `REDIS_SSL`: Enable SSL for Redis connection (default: `false`)

### Cache Settings
- `CACHE_ENABLED`: Enable/disable caching (default: `true`)
- `CACHE_LLM_TTL`: Time-to-live for LLM cache in seconds (default: `3600` - 1 hour)
- `CACHE_EMBEDDING_TTL`: Time-to-live for embedding cache in seconds (default: `86400` - 24 hours)

### API Authentication
- `API_KEY`: API key for protected endpoints (optional, if not set, endpoints are unprotected)

### Server Settings
- `HOST`: Server host (default: `0.0.0.0`)
- `PORT`: Server port (default: `8000`)
- `DEBUG`: Enable debug mode (default: `false`)

## Running the Application

### Using Docker Compose
```bash
docker-compose up -d
```

Access the application at `http://localhost:8000`

### Development Mode (Manual)
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode (Manual)
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Public Endpoints

#### `GET /`
Get application information
```bash
curl http://localhost:8000/
```

#### `GET /health`
Health check endpoint
```bash
curl http://localhost:8000/health
```

#### `POST /llm/generate`
Generate LLM response with caching
```bash
curl -X POST "http://localhost:8000/llm/generate?prompt=What%20is%20AI&context=general&model=gpt-4"
```

Parameters:
- `prompt` (required): The prompt text
- `context` (optional): Additional context
- `model` (optional): Model name (default: `default`)
- `bypass_cache` (optional): Skip cache lookup (default: `false`)

#### `POST /embedding/generate`
Generate embedding with caching
```bash
curl -X POST "http://localhost:8000/embedding/generate?text=Hello%20world&model=ada-002"
```

Parameters:
- `text` (required): Text to embed
- `model` (optional): Model name (default: `default`)
- `bypass_cache` (optional): Skip cache lookup (default: `false`)

#### `GET /metrics`
Prometheus metrics endpoint
```bash
curl http://localhost:8000/metrics
```

### Protected Endpoints (Require API Key)

Set the `X-API-Key` header with your API key for these endpoints.

#### `GET /cache/stats`
Get cache statistics
```bash
curl -H "X-API-Key: your_secret_api_key" http://localhost:8000/cache/stats
```

Response:
```json
{
  "llm": {
    "hits": 150,
    "misses": 50
  },
  "embedding": {
    "hits": 80,
    "misses": 20
  },
  "total": {
    "hits": 230,
    "misses": 70,
    "requests": 300,
    "hit_rate": 76.67
  }
}
```

#### `POST /cache/clear`
Clear all cache entries
```bash
curl -X POST -H "X-API-Key: your_secret_api_key" http://localhost:8000/cache/clear
```

Response:
```json
{
  "message": "Cache cleared successfully",
  "deleted_keys": 42
}
```

## How Caching Works

### Cache Key Generation
Cache keys are generated using SHA-256 hashing of the input parameters:

**For LLM responses:**
- Key format: `llm:<hash(prompt + context + model)>`
- Parameters: prompt, context, model name
- TTL: Configurable via `CACHE_LLM_TTL` (default: 1 hour)

**For embeddings:**
- Key format: `embedding:<hash(text + model)>`
- Parameters: text, model name
- TTL: Configurable via `CACHE_EMBEDDING_TTL` (default: 24 hours)

### Cache Flow

1. **Request arrives** with parameters (prompt/text, context, model)
2. **Hash generation**: SHA-256 hash of parameters creates cache key
3. **Cache lookup**: Check Redis for existing cached result
4. **Cache hit**: Return cached result immediately (fast path)
5. **Cache miss**: Execute function, cache result, return to client
6. **TTL expiration**: Cached entries automatically expire after TTL

### When to Bypass Cache

Use `bypass_cache=true` parameter when:

- **Real-time data required**: Need the most current response
- **Non-deterministic operations**: Function has side effects
- **Testing/debugging**: Want to verify actual function behavior
- **Cache invalidation**: Need to refresh specific cached entries

Example:
```bash
curl -X POST "http://localhost:8000/llm/generate?prompt=Current%20time&bypass_cache=true"
```

### Using Cache Decorators

The caching system provides two decorators for easy integration:

#### `@cache_llm_response`
```python
from app.cache import cache_llm_response

@cache_llm_response
async def my_llm_function(prompt: str, context: str = "", model: str = "", bypass_cache: bool = False):
    # Your LLM logic here
    return {"response": "..."}
```

#### `@cache_embedding`
```python
from app.cache import cache_embedding

@cache_embedding
async def my_embedding_function(text: str, model: str = "", bypass_cache: bool = False):
    # Your embedding logic here
    return {"embedding": [...]}
```

## Monitoring

### Prometheus Metrics

The application exposes the following Prometheus metrics at `/metrics`:

- `cache_hits_total{cache_type="llm|embedding"}`: Total cache hits by type
- `cache_misses_total{cache_type="llm|embedding"}`: Total cache misses by type
- `cache_hit_rate`: Overall cache hit rate percentage

### Example Prometheus Queries

```promql
# Cache hit rate
cache_hit_rate

# LLM cache hit rate
rate(cache_hits_total{cache_type="llm"}[5m]) / 
(rate(cache_hits_total{cache_type="llm"}[5m]) + rate(cache_misses_total{cache_type="llm"}[5m]))

# Total cache operations
sum(cache_hits_total) + sum(cache_misses_total)
```

## Testing

Run tests with pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_cache.py

# Run specific test
pytest tests/test_cache.py::test_cache_stats
```

### Test Requirements
Tests use `fakeredis` to simulate Redis without requiring a running Redis instance.

## Development

### Project Structure
```
aurea-orchestrator/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application
│   ├── config.py         # Configuration management
│   ├── cache.py          # Cache manager and decorators
│   ├── metrics.py        # Prometheus metrics
│   └── auth.py           # Authentication utilities
├── tests/
│   ├── conftest.py       # Test configuration
│   ├── test_cache.py     # Cache tests
│   └── test_api.py       # API endpoint tests
├── .env.example          # Example environment variables
├── requirements.txt      # Production dependencies
├── requirements-dev.txt  # Development dependencies
└── README.md            # This file
```

### Adding New Cached Endpoints

1. Import the decorator:
```python
from app.cache import cache_llm_response, cache_embedding
```

2. Apply to your async function:
```python
@cache_llm_response
async def my_endpoint(prompt: str, context: str = "", model: str = "", bypass_cache: bool = False):
    # Your logic here
    pass
```

3. Ensure function parameters include:
   - Required caching parameters (prompt/text, model)
   - Optional `bypass_cache` parameter

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
