# Aurea Orchestrator

**Automated Unified Reasoning & Execution Agents**

A comprehensive evaluation system for testing and monitoring AI agent performance with golden test cases, regression testing, and detailed scorecards.

## Features

- ✅ **Golden Test Cases**: Curated test cases for each agent feature type
- ✅ **Regression Testing**: Ensure agents don't regress in capability over time
- ✅ **Scorecard Metrics**: Track accuracy, latency, and cost for each evaluation
- ✅ **REST API**: `/eval/run` endpoint to trigger evaluation suites
- ✅ **Postgres Storage**: Persistent storage of all evaluation results
- ✅ **Grafana Dashboard**: Real-time visualization of evaluation trends

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- (Optional) Grafana for dashboards

### Installation

1. Clone the repository:
```bash
git clone https://github.com/andres20980/aurea-orchestrator.git
cd aurea-orchestrator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp config/.env.example .env
# Edit .env with your database credentials
```

4. Initialize the database:
```bash
# Create the database
createdb aurea_evals

# Tables will be created automatically on first run
```

### Running the API Server

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

Visit `http://localhost:8000/docs` for interactive API documentation.

## Usage

### Running Evaluations

**Run all evaluations:**
```bash
curl -X POST http://localhost:8000/eval/run \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Run evaluations for a specific feature:**
```bash
curl -X POST http://localhost:8000/eval/run \
  -H "Content-Type: application/json" \
  -d '{"feature_type": "code_generation"}'
```

**Run only golden tests:**
```bash
curl -X POST http://localhost:8000/eval/run \
  -H "Content-Type: application/json" \
  -d '{"test_type": "golden"}'
```

### Viewing Results

**List recent evaluation runs:**
```bash
curl http://localhost:8000/eval/runs
```

**Get details of a specific run:**
```bash
curl http://localhost:8000/eval/runs/{run_id}
```

**Get individual test results:**
```bash
curl http://localhost:8000/eval/results/{run_id}
```

## Architecture

```
aurea-orchestrator/
├── src/
│   ├── api/              # FastAPI routes
│   ├── database/         # Database models and connection
│   ├── eval/             # Evaluation framework
│   │   ├── golden_cases/ # Test cases by feature type
│   │   ├── runner.py     # Evaluation execution
│   │   └── scorecard.py  # Metrics calculation
│   └── models/           # Pydantic models
├── tests/
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests
├── config/               # Configuration files
├── grafana/              # Grafana dashboard
└── main.py               # Application entry point
```

## Evaluation Metrics

### Accuracy
- Measures how well agent output matches expected output
- Range: 0.0 to 1.0
- Threshold: 0.8 (configurable)

### Latency
- Time taken to execute the agent task
- Measured in milliseconds
- Includes full request/response cycle

### Cost
- Estimated cost based on token usage
- Calculated using configurable token rates
- Tracked per test and aggregated per run

## Feature Types

The system supports evaluation for the following agent capabilities:

- **Code Generation**: Creating code from natural language descriptions
- **Code Review**: Identifying issues and suggesting improvements
- **Debugging**: Finding and fixing bugs in code
- **Testing**: Generating and running tests
- **Documentation**: Creating and updating documentation
- **Refactoring**: Improving code structure and quality

## Database Schema

### eval_runs
Stores information about each evaluation run:
- `run_id`: Unique identifier
- `status`: pending, running, completed, failed
- `feature_type`: Optional filter
- `total_cases`, `passed_cases`, `failed_cases`
- `average_accuracy`, `average_latency`, `total_cost`
- `started_at`, `completed_at`

### eval_results
Stores individual test results:
- `case_id`: Test case identifier
- `feature_type`: Feature being tested
- `test_type`: golden or regression
- `input_data`, `expected_output`, `actual_output`
- `passed`, `accuracy`, `latency_ms`, `cost`
- `executed_at`

## Grafana Dashboard

The included Grafana dashboard provides:

1. **Accuracy Trend**: Track accuracy over time
2. **Latency Trend**: Monitor performance changes
3. **Cost Trend**: Keep track of API costs
4. **Pass Rate by Feature**: Compare feature performance
5. **Recent Runs**: Table of latest evaluations
6. **Accuracy Distribution**: Histogram of scores
7. **Test Type Distribution**: Golden vs regression breakdown

See [grafana/README.md](grafana/README.md) for setup instructions.

## Testing

Run unit tests:
```bash
pytest tests/unit -v
```

Run integration tests:
```bash
pytest tests/integration -v
```

Run all tests:
```bash
pytest tests/ -v
```

## Development

### Adding New Test Cases

1. Create or edit files in `src/eval/golden_cases/`
2. Follow the test case structure:
```python
{
    "case_id": "unique_id",
    "feature_type": "feature_name",
    "test_type": "golden",
    "description": "What this tests",
    "input_data": {...},
    "expected_output": {...},
    "metadata": {...}
}
```

### Adding New Features

1. Add feature to `FeatureType` enum in `src/models/eval_models.py`
2. Create golden cases file in `src/eval/golden_cases/`
3. Import in `src/eval/golden_cases/__init__.py`

## API Documentation

Full API documentation is available at `/docs` when running the server.

Key endpoints:
- `POST /eval/run` - Run evaluation suite
- `GET /eval/runs` - List evaluation runs
- `GET /eval/runs/{run_id}` - Get run details
- `GET /eval/results/{run_id}` - Get test results

## Configuration

Configuration is managed through environment variables (see `config/.env.example`):

- `DATABASE_URL`: PostgreSQL connection string
- `API_HOST`, `API_PORT`: API server settings
- `DEFAULT_ACCURACY_THRESHOLD`: Pass/fail threshold
- `COST_PER_1K_INPUT_TOKENS`, `COST_PER_1K_OUTPUT_TOKENS`: Pricing

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request
