# Aurea Orchestrator

Automated Unified Reasoning & Execution Agents - A Multi-Agent Orchestration System

## Overview

Aurea Orchestrator is a sophisticated multi-agent system built with FastAPI, LangGraph, Celery, Redis, and PostgreSQL. It orchestrates five specialized agents to collaboratively solve complex tasks through context analysis, architecture design, code generation, testing, and review.

## Architecture

### Components

- **FastAPI**: REST API server for task submission and retrieval
- **LangGraph**: Workflow orchestration for multi-agent collaboration
- **Celery**: Distributed task queue for async processing
- **Redis**: Message broker and result backend
- **PostgreSQL**: Data persistence (future enhancement)
- **Model Router**: Intelligent routing between Claude (complex tasks) and DeepSeek/GPT (simple tasks)

### Agents

1. **Context Agent**: Analyzes task requirements and provides comprehensive context
2. **Architect Agent**: Designs system architecture and technical approach
3. **Code Agent**: Generates clean, well-documented code
4. **Test Agent**: Creates comprehensive unit and integration tests
5. **Review Agent**: Reviews code quality, security, and best practices

## Workflow

```
Task Submission → Context Analysis → Architecture Design → Code Generation → Test Creation → Code Review → Results
```

The workflow is orchestrated using LangGraph, ensuring proper sequencing and state management between agents.

## Setup

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- API keys for Anthropic (Claude) and OpenAI

### Installation

#### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/andres20980/aurea-orchestrator.git
cd aurea-orchestrator
```

2. Create `.env` file from the example:
```bash
cp .env.example .env
```

3. Edit `.env` and add your API keys:
```
ANTHROPIC_API_KEY=your-anthropic-api-key
OPENAI_API_KEY=your-openai-api-key
```

4. Start the services:
```bash
docker-compose up -d
```

The API will be available at `http://localhost:8000`

#### Local Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements-dev.txt
```

3. Start Redis and PostgreSQL (using Docker):
```bash
docker-compose up -d redis postgres
```

4. Run the API server:
```bash
uvicorn aurea_orchestrator.main:app --reload
```

5. In another terminal, start the Celery worker:
```bash
celery -A aurea_orchestrator.celery_app worker --loglevel=info
```

## API Endpoints

### Health Check

```http
GET /health
```

Returns the health status of the API.

**Response:**
```json
{
  "status": "healthy"
}
```

### Create Task

```http
POST /tasks
```

Submit a new task for processing.

**Request Body:**
```json
{
  "description": "Create a Python function to calculate factorial",
  "metadata": {
    "requires_reasoning": true
  }
}
```

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "result": null
}
```

### Get Task Status

```http
GET /tasks/{task_id}
```

Retrieve the current status of a task.

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "result": {
    "context": "...",
    "architecture": "...",
    "code": "...",
    "tests": "...",
    "review": "..."
  }
}
```

### Get Task Results

```http
GET /tasks/{task_id}/result
```

Retrieve detailed results of a completed task.

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "context": "Task requires a recursive or iterative approach...",
  "architecture": "Function-based design with error handling...",
  "code": "def factorial(n): ...",
  "tests": "def test_factorial(): ...",
  "review": "Code quality: Excellent. Test coverage: 100%..."
}
```

## Model Router

The Model Router intelligently selects between Claude and DeepSeek based on task complexity:

- **Claude (Complex)**: Used for tasks requiring deep reasoning, architecture design, complex algorithms
- **DeepSeek/GPT (Simple)**: Used for straightforward tasks, simple fixes, documentation updates

### Complexity Factors

- Task description length
- Presence of complex keywords (architecture, design pattern, refactor, optimize, etc.)
- Metadata flags (`requires_reasoning`, `multi_agent`)

### Configuration

Adjust the complexity threshold in `.env`:
```
COMPLEXITY_THRESHOLD=0.5  # Range: 0.0-1.0
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=aurea_orchestrator --cov-report=html

# Run specific test file
pytest tests/test_model_router.py
```

### Code Formatting and Linting

```bash
# Format code with black
black aurea_orchestrator tests

# Lint with ruff
ruff check aurea_orchestrator tests

# Auto-fix issues
ruff check --fix aurea_orchestrator tests
```

### Project Structure

```
aurea-orchestrator/
├── aurea_orchestrator/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── schemas.py           # Pydantic models
│   ├── model_router.py      # Model selection logic
│   ├── agents.py            # Agent implementations
│   ├── workflow.py          # LangGraph workflow
│   └── celery_app.py        # Celery configuration
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Test fixtures
│   ├── test_model_router.py
│   ├── test_agents.py
│   ├── test_workflow.py
│   ├── test_api.py
│   └── test_schemas.py
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## Usage Examples

### Example 1: Simple Task

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Create a function to check if a number is prime"
  }'
```

### Example 2: Complex Task

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Design and implement a distributed caching system with Redis, including architecture, implementation, and comprehensive tests",
    "metadata": {
      "requires_reasoning": true,
      "multi_agent": true
    }
  }'
```

### Example 3: Check Task Status

```bash
curl http://localhost:8000/tasks/550e8400-e29b-41d4-a716-446655440000
```

## Testing Strategy

The project follows Test-Driven Development (TDD) principles:

1. **Unit Tests**: Test individual components (agents, model router, schemas)
2. **Integration Tests**: Test workflow orchestration
3. **API Tests**: Test FastAPI endpoints
4. **Coverage**: Aim for >80% test coverage

## Future Enhancements

- [ ] Database integration for task persistence
- [ ] WebSocket support for real-time updates
- [ ] Web UI for task management
- [ ] Support for additional LLM providers
- [ ] Advanced caching strategies
- [ ] Metrics and monitoring
- [ ] Authentication and authorization
- [ ] Rate limiting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run linting and tests
5. Submit a pull request

## License

MIT License

## Contact

For questions and support, please open an issue on GitHub.
