# Aurea Orchestrator

Automated Unified Reasoning & Execution Agents - A robust orchestration system for managing AI model jobs with comprehensive cost tracking, rate limiting, and reliability features.

## Features

- **Cost Tracking**: Track estimated costs per job and automatically abort when exceeding configurable limits
- **Rate Limiting**: Per-model RPM (Requests Per Minute) and TPM (Tokens Per Minute) rate limiting
- **Retry Mechanism**: Automatic retries with exponential backoff for transient failures
- **Circuit Breaker**: Prevent cascading failures with circuit breaker pattern
- **PII Redaction**: Automatic redaction of Personally Identifiable Information in logs
- **Model Allow/Deny Lists**: Control which models can be used in your orchestrator
- **Security**: Pre-commit hooks with Bandit and Semgrep for security scanning

## Installation

```bash
pip install -e .
```

For development:

```bash
pip install -e ".[dev]"
```

## Quick Start

```python
from aurea import Orchestrator

# Initialize orchestrator for a job
orch = Orchestrator(job_id="my-job-1", max_cost=5.0)

# Define your model request function
def call_model():
    # Your model API call here
    return {"response": "Hello world"}

# Execute request with automatic cost tracking, rate limiting, and retry
result = orch.execute_request(
    model="gpt-3.5-turbo",
    input_tokens=100,
    output_tokens=50,
    request_func=call_model
)

# Check status
status = orch.get_status()
print(f"Total cost: ${status['cost_summary']['total_cost']:.4f}")
```

## Environment Variables

### Cost Limits

- `MAX_JOB_COST` (default: `10.0`)
  - Maximum cost per job in USD before aborting
  - Type: float
  - Example: `MAX_JOB_COST=25.0`

### Rate Limiting

- `DEFAULT_RPM` (default: `60`)
  - Default requests per minute limit for all models
  - Type: integer
  - Example: `DEFAULT_RPM=120`

- `DEFAULT_TPM` (default: `100000`)
  - Default tokens per minute limit for all models
  - Type: integer
  - Example: `DEFAULT_TPM=200000`

### Retry Configuration

- `MAX_RETRIES` (default: `3`)
  - Maximum number of retry attempts for failed requests
  - Type: integer
  - Example: `MAX_RETRIES=5`

- `RETRY_BASE_DELAY` (default: `1.0`)
  - Base delay in seconds for exponential backoff
  - Type: float
  - Example: `RETRY_BASE_DELAY=2.0`

- `RETRY_MAX_DELAY` (default: `60.0`)
  - Maximum delay in seconds for exponential backoff
  - Type: float
  - Example: `RETRY_MAX_DELAY=120.0`

### Circuit Breaker

- `CIRCUIT_BREAKER_THRESHOLD` (default: `5`)
  - Number of consecutive failures before circuit opens
  - Type: integer
  - Example: `CIRCUIT_BREAKER_THRESHOLD=10`

- `CIRCUIT_BREAKER_TIMEOUT` (default: `60.0`)
  - Timeout in seconds before attempting to close circuit
  - Type: float
  - Example: `CIRCUIT_BREAKER_TIMEOUT=120.0`

### Model Allow/Deny Lists

- `ALLOWED_MODELS` (default: `None`)
  - Comma-separated list of allowed models (if set, only these models can be used)
  - Type: string (comma-separated)
  - Example: `ALLOWED_MODELS=gpt-4,gpt-3.5-turbo,claude-3-sonnet`

- `DENIED_MODELS` (default: `None`)
  - Comma-separated list of denied models (takes precedence over allowed list)
  - Type: string (comma-separated)
  - Example: `DENIED_MODELS=unsafe-model,deprecated-model`

### Logging

- `LOG_LEVEL` (default: `INFO`)
  - Logging level
  - Type: string
  - Options: `DEBUG`, `INFO`, `WARNING`, `ERROR`
  - Example: `LOG_LEVEL=DEBUG`

- `REDACT_PII` (default: `true`)
  - Whether to redact Personally Identifiable Information in logs
  - Type: boolean
  - Options: `true`, `false`
  - Example: `REDACT_PII=false`

## Configuration File

You can also use a `.env` file in your project root:

```bash
# .env
MAX_JOB_COST=15.0
DEFAULT_RPM=120
DEFAULT_TPM=150000
MAX_RETRIES=5
CIRCUIT_BREAKER_THRESHOLD=10
ALLOWED_MODELS=gpt-4,gpt-3.5-turbo,claude-3-sonnet
REDACT_PII=true
LOG_LEVEL=INFO
```

## Components

### Cost Tracker

Tracks estimated costs for each model request and enforces limits:

```python
from aurea import CostTracker

tracker = CostTracker(job_id="job-1", max_cost=10.0)

# Track usage
cost = tracker.track_usage(
    model="gpt-3.5-turbo",
    input_tokens=1000,
    output_tokens=500
)

# Get summary
summary = tracker.get_summary()
print(f"Total cost: ${summary['total_cost']:.4f}")
```

### Rate Limiter

Enforces per-model rate limits:

```python
from aurea import RateLimiter

limiter = RateLimiter(default_rpm=60, default_tpm=100000)

# Set custom limits for specific model
limiter.set_model_limits("gpt-4", rpm=10, tpm=50000)

# Check and wait if necessary
limiter.check_and_wait(model="gpt-4", tokens=1000)
```

### Circuit Breaker

Prevents cascading failures:

```python
from aurea import CircuitBreaker

breaker = CircuitBreaker(name="my-service", failure_threshold=5, timeout=60.0)

# Call function through circuit breaker
result = breaker.call(my_function, arg1, arg2)

# Check state
state = breaker.get_state()
print(f"Circuit state: {state['state']}")
```

## Security Features

### Pre-commit Hooks

Install pre-commit hooks for automatic security scanning:

```bash
pip install pre-commit
pre-commit install
```

This will run:
- **Bandit**: Python security linter
- **Semgrep**: Static analysis for finding bugs and security issues
- **Black**: Code formatter
- **isort**: Import sorter
- **flake8**: Style guide enforcement

### PII Redaction

Automatic PII redaction in logs protects sensitive information:

```python
from aurea.pii_redactor import PIIRedactor

# Redact text
text = "Contact me at user@example.com or 555-123-4567"
redacted = PIIRedactor.redact(text)
# Result: "Contact me at [EMAIL_REDACTED] or [PHONE_REDACTED]"

# Redact dictionaries
data = {"email": "user@example.com", "password": "secret123"}
redacted = PIIRedactor.redact_dict(data)
# Result: {"email": "[EMAIL_REDACTED]", "password": "[REDACTED]"}
```

Redacts:
- Email addresses
- Phone numbers
- Social Security Numbers
- Credit card numbers
- IP addresses
- API keys and tokens
- Passwords and secrets

## Testing

Run tests:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=aurea --cov-report=html
```

Run security scans:

```bash
# Bandit
bandit -r src/ -c .bandit.yml

# Semgrep
semgrep --config=auto src/
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/andres20980/aurea-orchestrator.git
cd aurea-orchestrator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Code Quality

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint
flake8 src/ tests/

# Type check
mypy src/
```

## Architecture

```
aurea-orchestrator/
├── src/aurea/
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── orchestrator.py        # Main orchestrator
│   ├── cost_tracker.py        # Cost tracking
│   ├── rate_limiter.py        # Rate limiting
│   ├── circuit_breaker.py     # Circuit breaker pattern
│   ├── retry_handler.py       # Retry with exponential backoff
│   ├── pii_redactor.py        # PII redaction
│   └── logger.py              # Structured logging
├── tests/                     # Test suite
├── .pre-commit-config.yaml    # Pre-commit hooks
├── .bandit.yml                # Bandit configuration
└── README.md                  # This file
```

## License

MIT License

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and security scans
5. Submit a pull request

## Support

For issues and questions, please use the GitHub issue tracker.
