# aurea-orchestrator
Automated Unified Reasoning &amp; Execution Agents

## Overview

The Aurea Orchestrator is a FastAPI-based workflow orchestration system that uses LangGraph to manage parallel phase execution for automated reasoning and execution tasks.

## Features

- **Parallel Phase Execution**: Supports concurrent execution of test and review_precheck phases
- **LangGraph Workflow**: Implements a structured workflow with nodes: plan, implement, test, review_precheck, and review
- **Iterative Processing**: Automatically loops back for improvements based on review decisions
- **Status Tracking**: Real-time progress monitoring for each workflow node
- **RESTful API**: Clean API endpoints for job creation and status monitoring

## Workflow

The orchestrator follows this workflow pattern:

```
plan → implement → {test, review_precheck} → review
                            ↓
                    (if REJECTED & iterations < max)
                            ↓
                          plan (loop back)
```

### Nodes

1. **plan**: Generates an implementation plan based on input data
2. **implement**: Executes the plan
3. **test**: Runs tests on the implementation (executes in parallel with review_precheck)
4. **review_precheck**: Performs preliminary review checks (executes in parallel with test)
5. **review**: Makes final review decision (APPROVED or REJECTED)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Start the Server

```bash
python main.py
```

Or with uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### API Endpoints

#### Create a Job

```bash
POST /jobs
```

Request body:
```json
{
  "input_data": {
    "task": "Your task description"
  },
  "max_iterations": 3
}
```

Response:
```json
{
  "job_id": "uuid-string",
  "status": "pending",
  "created_at": "2025-11-11T08:48:13.051Z"
}
```

#### Get Job Status

```bash
GET /jobs/{job_id}/status
```

Response:
```json
{
  "job_id": "uuid-string",
  "status": "running",
  "current_node": "implement",
  "iteration_count": 1,
  "max_iterations": 3,
  "node_progress": [
    {
      "node_name": "plan",
      "status": "completed",
      "start_time": "2025-11-11T08:48:13.051Z",
      "end_time": "2025-11-11T08:48:13.551Z",
      "output": "Plan created for: Your task description",
      "error": null
    }
  ],
  "created_at": "2025-11-11T08:48:13.051Z",
  "updated_at": "2025-11-11T08:48:14.051Z"
}
```

## Testing

Run tests with pytest:

```bash
pytest test_orchestrator.py -v
```

## Architecture

- **main.py**: FastAPI application with REST endpoints
- **workflow.py**: LangGraph workflow definition and node implementations
- **models.py**: Data models and type definitions
- **storage.py**: In-memory job storage and state management
- **test_orchestrator.py**: Test suite

## Dependencies

- FastAPI: Web framework
- LangGraph: Workflow orchestration
- Pydantic: Data validation
- Uvicorn: ASGI server

## License

MIT
