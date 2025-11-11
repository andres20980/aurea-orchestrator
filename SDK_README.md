# Aurea Client SDK

Python client library for interacting with the Aurea Orchestrator API.

## Overview

The Aurea Client SDK provides a simple and intuitive interface for submitting orchestration requests, checking their status, and managing approvals through the Aurea Orchestrator API.

## Installation

### From PyPI (when published)

```bash
pip install aurea-client
```

### From source

```bash
git clone https://github.com/andres20980/aurea-orchestrator.git
cd aurea-orchestrator
pip install -e .
```

## Quick Start

```python
from aurea_client import AureaClient

# Initialize the client
client = AureaClient(
    base_url="http://localhost:8000",
    api_key="your-api-key-here"
)

# Submit a new orchestration request
response = client.request(
    task_description="Analyze customer data",
    parameters={"dataset": "customers.csv"},
    priority=5
)
print(f"Request ID: {response['request_id']}")

# Check request status
status = client.status(response['request_id'])
print(f"Status: {status['status']}")

# Approve the request
approval = client.approve(
    request_id=response['request_id'],
    approved=True,
    comment="Approved for processing"
)
print(f"Approved: {approval['message']}")

# Clean up
client.close()
```

## Authentication

The Aurea Client SDK uses API key authentication. You need to provide your API key when initializing the client:

```python
client = AureaClient(
    base_url="http://localhost:8000",
    api_key="aurea-demo-api-key-12345"
)
```

The API key is sent in the `X-API-Key` header with each request.

### Demo API Key

For development and testing, you can use the demo API key:
```
aurea-demo-api-key-12345
```

⚠️ **Note**: In production, use secure, unique API keys and never commit them to version control.

## API Methods

### `request(task_description, parameters=None, priority=1)`

Submit a new orchestration request.

**Parameters:**
- `task_description` (str): Description of the task to orchestrate
- `parameters` (dict, optional): Task parameters as a dictionary
- `priority` (int, optional): Task priority from 1-10 (default: 1)

**Returns:**
- Dictionary with `request_id`, `status`, `message`, and `created_at`

**Example:**
```python
response = client.request(
    task_description="Generate monthly report",
    parameters={
        "report_type": "sales",
        "month": "November",
        "year": 2024
    },
    priority=8
)
```

### `status(request_id)`

Get the status of an orchestration request.

**Parameters:**
- `request_id` (str): Unique identifier of the request

**Returns:**
- Dictionary with `request_id`, `status`, `task_description`, `created_at`, `updated_at`, and `result`

**Example:**
```python
status_info = client.status("550e8400-e29b-41d4-a716-446655440000")
print(f"Current status: {status_info['status']}")
if status_info['result']:
    print(f"Result: {status_info['result']}")
```

### `approve(request_id, approved, comment=None)`

Approve or reject an orchestration request.

**Parameters:**
- `request_id` (str): Unique identifier of the request
- `approved` (bool): True to approve, False to reject
- `comment` (str, optional): Comment explaining the decision

**Returns:**
- Dictionary with `request_id`, `status`, and `message`

**Examples:**
```python
# Approve a request
approval = client.approve(
    request_id="550e8400-e29b-41d4-a716-446655440000",
    approved=True,
    comment="Looks good, proceed with processing"
)

# Reject a request
rejection = client.approve(
    request_id="550e8400-e29b-41d4-a716-446655440000",
    approved=False,
    comment="Insufficient resources"
)
```

## Request Status Values

Requests can have the following statuses:

- **pending**: Request submitted and awaiting approval
- **approved**: Request approved and ready for processing
- **rejected**: Request rejected and will not be processed
- **processing**: Request is currently being processed
- **completed**: Request processing completed successfully
- **failed**: Request processing failed

## Context Manager Usage

The client can be used as a context manager to automatically handle cleanup:

```python
with AureaClient(base_url="http://localhost:8000", api_key="your-api-key") as client:
    response = client.request("Process data", {"source": "db"})
    status = client.status(response['request_id'])
    # Client automatically closed when exiting the context
```

## Error Handling

The SDK raises standard `requests` library exceptions:

```python
from requests.exceptions import HTTPError

try:
    client = AureaClient(base_url="http://localhost:8000", api_key="invalid-key")
    response = client.request("Test task")
except HTTPError as e:
    if e.response.status_code == 401:
        print("Authentication failed - invalid API key")
    elif e.response.status_code == 404:
        print("Request not found")
    else:
        print(f"HTTP error occurred: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
```

## Examples

The `examples/` directory contains several usage examples:

- **basic_usage.py**: Basic workflow demonstration
- **advanced_usage.py**: Advanced features including error handling and multiple requests
- **authentication.py**: Authentication examples and patterns

To run the examples:

```bash
# Start the Aurea Orchestrator API server first
cd orchestrator
python -m pip install -r requirements.txt
python main.py

# In another terminal, run the examples
cd examples
python basic_usage.py
python advanced_usage.py
python authentication.py
```

## Configuration

### Timeout

You can configure the request timeout:

```python
client = AureaClient(
    base_url="http://localhost:8000",
    api_key="your-api-key",
    timeout=60  # 60 seconds timeout
)
```

### Base URL

The base URL should point to your Aurea Orchestrator API server:

```python
# Local development
client = AureaClient(base_url="http://localhost:8000", api_key="key")

# Production
client = AureaClient(base_url="https://api.aurea.example.com", api_key="key")
```

## Development

### Setting up development environment

```bash
# Clone the repository
git clone https://github.com/andres20980/aurea-orchestrator.git
cd aurea-orchestrator

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

### Running tests

```bash
pytest
```

### Code formatting

```bash
black aurea_client/
```

### Type checking

```bash
mypy aurea_client/
```

## Requirements

- Python 3.8 or higher
- requests >= 2.28.0

## License

MIT License

## Support

For issues and questions:
- GitHub Issues: https://github.com/andres20980/aurea-orchestrator/issues
- Documentation: https://github.com/andres20980/aurea-orchestrator#readme

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
