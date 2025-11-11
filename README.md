# Aurea Orchestrator

Automated Unified Reasoning & Execution Agents - A comprehensive orchestration platform with REST API and Python SDK.

## Overview

Aurea Orchestrator provides a robust API for managing and orchestrating automated tasks with built-in approval workflows, status tracking, and authentication.

## Features

- 🚀 **RESTful API** - FastAPI-based service with automatic OpenAPI documentation
- 🐍 **Python SDK** - Easy-to-use client library (`aurea-client`)
- 🔐 **Authentication** - API key-based authentication
- ✅ **Approval Workflow** - Built-in request approval system
- 📊 **Status Tracking** - Real-time status updates for all requests
- 📝 **OpenAPI Spec** - Auto-generated OpenAPI 3.0 specification
- 📚 **Comprehensive Examples** - Multiple usage examples included

## Quick Start

### 1. Start the API Server

```bash
cd orchestrator
pip install -r requirements.txt
python main.py
```

The API server will start at `http://localhost:8000`

### 2. View API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

### 3. Install the Python SDK

```bash
pip install -e .
```

### 4. Use the SDK

```python
from aurea_client import AureaClient

# Initialize client
client = AureaClient(
    base_url="http://localhost:8000",
    api_key="aurea-demo-api-key-12345"
)

# Submit a request
response = client.request(
    task_description="Analyze customer data",
    parameters={"dataset": "customers.csv"}
)

# Check status
status = client.status(response['request_id'])

# Approve request
approval = client.approve(
    request_id=response['request_id'],
    approved=True
)
```

## Project Structure

```
aurea-orchestrator/
├── orchestrator/          # FastAPI application
│   ├── main.py           # Main API server
│   ├── __init__.py       # Package init
│   └── requirements.txt  # API dependencies
├── aurea_client/         # Python SDK
│   ├── __init__.py       # SDK implementation
│   └── requirements.txt  # SDK dependencies
├── examples/             # Usage examples
│   ├── basic_usage.py    # Basic workflow
│   ├── advanced_usage.py # Advanced features
│   └── authentication.py # Auth examples
├── pyproject.toml        # SDK package configuration
├── SDK_README.md         # SDK documentation
└── README.md            # This file
```

## API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Service information |
| POST | `/request` | Submit orchestration request |
| GET | `/status/{request_id}` | Get request status |
| POST | `/approve` | Approve/reject request |

### OpenAPI Documentation

| Endpoint | Description |
|----------|-------------|
| `/docs` | Interactive Swagger UI |
| `/redoc` | ReDoc documentation |
| `/openapi.json` | OpenAPI specification |

## SDK Methods

The `aurea-client` SDK provides three main methods:

### `request(task_description, parameters=None, priority=1)`
Submit a new orchestration request.

### `status(request_id)`
Get the current status of a request.

### `approve(request_id, approved, comment=None)`
Approve or reject a pending request.

See [SDK_README.md](SDK_README.md) for detailed documentation.

## Authentication

All API endpoints (except `/` and documentation endpoints) require authentication via API key in the `X-API-Key` header.

**Demo API Key:** `aurea-demo-api-key-12345`

Example:
```bash
curl -X POST "http://localhost:8000/request" \
  -H "X-API-Key: aurea-demo-api-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "task_description": "Test task",
    "parameters": {},
    "priority": 1
  }'
```

## Examples

Run the included examples to see the SDK in action:

```bash
# Start the API server first
cd orchestrator
python main.py

# In another terminal, run examples
cd examples
python basic_usage.py
python advanced_usage.py
python authentication.py
```

## Development

### Install Development Dependencies

```bash
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

## Requirements

- Python 3.8+
- FastAPI
- Uvicorn
- Pydantic
- Requests

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on GitHub.
