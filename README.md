# aurea-orchestrator
Automated Unified Reasoning & Execution Agents

## Overview

Aurea Orchestrator is a code review automation system that performs comprehensive quality checks on Python projects.

## Features

- **Automated Code Review**: Comprehensive code quality assessment
- **Coverage Analysis**: Ensures code coverage meets minimum thresholds
- **Code Quality Checks**: Validates code formatting and style compliance
- **Security Scanning**: Detects high-severity security vulnerabilities

## Review Agent

The Review Agent performs automated code reviews based on the following criteria:

### Review Criteria

The review process checks four critical aspects:

1. **Code Coverage (≥70%)**
   - Measures test coverage percentage
   - Minimum threshold: 70%
   - Uses coverage.py for analysis
   - Reports actual coverage percentage

2. **Ruff Linting**
   - Fast Python linter
   - Checks code quality and style
   - Must pass with zero violations
   - Replaces multiple linters (flake8, isort, etc.)

3. **Black Formatting**
   - Ensures consistent code formatting
   - PEP 8 compliant
   - Must pass formatting checks
   - Line length: 88 characters (default)

4. **Bandit Security Scanning**
   - Detects security vulnerabilities
   - Zero HIGH severity issues allowed
   - MEDIUM and LOW issues reported but don't block approval

### Review Status

The Review Agent returns one of three statuses:

- **APPROVED**: All checks pass (coverage ≥70%, ruff passes, black passes, no HIGH security issues)
- **NEEDS_REVISION**: Code quality or coverage issues (but no critical security problems)
- **FAILED**: HIGH severity security issues detected (critical failure)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Command Line

Run a code review on the current directory:

```bash
python review_agent.py
```

Run a review with custom options:

```bash
python review_agent.py --path /path/to/project --coverage-threshold 80
```

Get JSON output:

```bash
python review_agent.py --json
```

### Python API

```python
from review_agent import ReviewAgent

# Create agent
agent = ReviewAgent(
    project_path=".",
    coverage_threshold=70.0
)

# Run review
result = agent.review()

# Check status
print(f"Status: {result.status.value}")
print(f"Coverage: {result.coverage_percentage}%")
print(f"Summary: {result.summary}")
```

### Integration with Job Status

```python
from job_status import JobStatus, JobState
from review_agent import ReviewAgent

# Create job
job = JobStatus(job_id="build-123", state=JobState.RUNNING)

# Run review
agent = ReviewAgent()
review_result = agent.review()

# Add review to job
job.add_review(review_result)
job.update_state(JobState.COMPLETED)

# Get formatted summary
print(job.get_review_summary())
```

## Development

### Running Tests

```bash
pytest
```

With coverage:

```bash
pytest --cov=. --cov-report=term-missing
```

### Code Quality Checks

Run all checks manually:

```bash
# Coverage
pytest --cov=. --cov-report=json

# Ruff
ruff check .

# Black
black --check .

# Bandit
bandit -r . -f json --severity-level high
```

## License

MIT License
