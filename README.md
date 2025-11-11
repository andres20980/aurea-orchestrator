# aurea-orchestrator
Automated Unified Reasoning &amp; Execution Agents

A system for managing AI agents with semantic versioning, job metadata tracking, and cross-run comparison capabilities.

## Features

- **Semantic Versioning for Agents**: Each agent (Architect, Code, Review, Test, Deploy) has its own semantic version (MAJOR.MINOR.PATCH)
- **Job Metadata Storage**: Track which agent versions were used in each job execution
- **Version Comparison**: Compare agent versions across different job runs
- **REST API**: HTTP endpoints for accessing agent versions and job metadata
- **CLI Tool**: Command-line interface for managing agents and jobs

## Agent Types

- **Architect**: System design and architecture planning (v1.0.0)
- **Code**: Code generation and modification (v1.0.0)
- **Review**: Code review and quality assurance (v1.0.0)
- **Test**: Testing and validation (v1.0.0)
- **Deploy**: Deployment operations (v1.0.0)

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### Running the Example

```bash
python example.py
```

This will:
1. Initialize agents with their versions
2. Create and execute a job
3. Store job metadata with agent versions
4. Create a second job for comparison
5. Compare versions across job runs

### Using the CLI

**View all agent versions:**
```bash
python cli.py agents-versions
```

**View specific agent version:**
```bash
python cli.py agent-version architect
```

**Compare semantic versions:**
```bash
python cli.py compare-versions 1.0.0 1.1.0
```

**List all jobs:**
```bash
python cli.py list-jobs
```

**View job details:**
```bash
python cli.py job-info job-001
```

**Compare two jobs:**
```bash
python cli.py compare-jobs job-001 job-002
```

**JSON output (for any command):**
```bash
python cli.py --json agents-versions
```

### Using the REST API

**Start the API server:**
```bash
python api.py
```

**Available endpoints:**

- `GET /agents/versions` - Get all agent versions
- `GET /agents/{agent_name}/version` - Get specific agent version
- `POST /versions/compare` - Compare two versions
- `GET /jobs` - List all jobs
- `GET /jobs/{job_id}` - Get job metadata
- `POST /jobs/compare` - Compare two job runs
- `GET /health` - Health check

**Example API calls:**

```bash
# Get all agent versions
curl http://localhost:5000/agents/versions

# Get specific agent version
curl http://localhost:5000/agents/architect/version

# Compare versions
curl -X POST http://localhost:5000/versions/compare \
  -H "Content-Type: application/json" \
  -d '{"version1": "1.0.0", "version2": "1.1.0"}'

# List jobs
curl http://localhost:5000/jobs

# Get job details
curl http://localhost:5000/jobs/job-001

# Compare jobs
curl -X POST http://localhost:5000/jobs/compare \
  -H "Content-Type: application/json" \
  -d '{"job1": "job-001", "job2": "job-002"}'
```

## Python API Usage

```python
from agents import ArchitectAgent, CodeAgent, ReviewAgent
from agents.versions import get_agent_version, get_all_agent_versions, compare_versions
from job_metadata import JobMetadata, JobMetadataStore

# Initialize agents
architect = ArchitectAgent()
print(f"Architect version: {architect.version}")

# Get all versions
versions = get_all_agent_versions()
print(versions)  # {'architect': '1.0.0', 'code': '1.0.0', ...}

# Compare versions
result = compare_versions('1.0.0', '1.1.0')
# Returns: -1 (less than), 0 (equal), or 1 (greater than)

# Create and track a job
job = JobMetadata('job-123', 'orchestration')
job.add_agent_version('architect', architect.version)
job.update_status('running')

# Execute task
task = {'type': 'design', 'spec': 'system architecture'}
result = architect.execute(task)
job.add_result(result)

job.update_status('completed')

# Save job metadata
store = JobMetadataStore()
store.save(job)

# Load and compare jobs
job1 = store.load('job-001')
comparison = store.compare_runs('job-001', 'job-002')
```

## Job Metadata Structure

Jobs are stored as JSON files in `.aurea/jobs/` directory:

```json
{
  "job_id": "job-001",
  "job_type": "orchestration",
  "created_at": "2025-11-11T08:58:46.707436+00:00",
  "updated_at": "2025-11-11T08:58:46.707503+00:00",
  "status": "completed",
  "agent_versions": {
    "architect": "1.0.0",
    "code": "1.0.0",
    "review": "1.0.0"
  },
  "results": [
    {
      "timestamp": "2025-11-11T08:58:46.707490+00:00",
      "data": {
        "status": "completed",
        "metadata": {...},
        "result": {...}
      }
    }
  ]
}
```

## Semantic Versioning

This project follows [Semantic Versioning](https://semver.org/) for agents:

- **MAJOR**: Breaking changes to agent interface or behavior
- **MINOR**: New features, backwards-compatible
- **PATCH**: Bug fixes, backwards-compatible

## Testing

Run all tests:

```bash
python -m unittest discover tests/ -v
```

Run specific test module:

```bash
python -m unittest tests.test_versions -v
python -m unittest tests.test_agents -v
python -m unittest tests.test_job_metadata -v
```

## Project Structure

```
aurea-orchestrator/
├── agents/
│   ├── __init__.py
│   ├── versions.py          # Version management
│   ├── architect.py          # Architect agent
│   ├── code.py              # Code agent
│   └── review.py            # Review agent
├── tests/
│   ├── test_versions.py     # Version tests
│   ├── test_agents.py       # Agent tests
│   └── test_job_metadata.py # Job metadata tests
├── job_metadata.py          # Job metadata management
├── cli.py                   # Command-line interface
├── api.py                   # REST API
├── example.py               # Example usage
├── requirements.txt         # Dependencies
├── setup.py                 # Package setup
└── README.md               # This file
```

## License

MIT
