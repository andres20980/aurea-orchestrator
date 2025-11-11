# Aurea Orchestrator

**Automated Unified Reasoning & Execution Agents**

A powerful orchestration platform with a built-in Prompt Registry for managing versioned YAML prompt templates with variable substitution.

## Features

- 🎯 **Prompt Registry**: Store and manage prompt templates with YAML format
- 📦 **Versioning**: Automatic versioning of prompt templates
- 🔄 **Variable Substitution**: Dynamic template rendering with Jinja2
- ✅ **Validation**: Built-in YAML and template syntax validation
- 👁️ **Preview**: Preview rendered templates before use
- 📊 **Job Tracking**: Track which prompt version was used per job
- 🚀 **REST API**: Full CRUD operations via FastAPI
- 🧪 **Comprehensive Tests**: Unit and integration tests included

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/andres20980/aurea-orchestrator.git
cd aurea-orchestrator

# Install dependencies
pip install -r requirements.txt
```

### Running the Server

```bash
# Run the FastAPI server
python -m aurea_orchestrator.main

# Or using uvicorn directly
uvicorn aurea_orchestrator.main:app --reload
```

The API will be available at `http://localhost:8000`

Interactive API documentation: `http://localhost:8000/docs`

## Prompt Registry

### Overview

The Prompt Registry allows you to manage prompt templates with:
- **YAML format**: Store prompts in structured YAML files
- **Versioning**: Automatic version tracking when updating templates
- **Variables**: Use Jinja2 syntax for dynamic content (e.g., `{{ variable_name }}`)
- **Validation**: Automatic validation of YAML syntax and template variables
- **Preview**: Test templates with sample variables before deployment

### Creating a Prompt Template

**API Request:**
```bash
curl -X POST "http://localhost:8000/prompts/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "greeting",
    "description": "A friendly greeting template",
    "template_yaml": "prompt: Hello {{ name }}! Welcome to {{ service }}.",
    "variables": ["name", "service"]
  }'
```

**Response:**
```json
{
  "id": 1,
  "name": "greeting",
  "version": 1,
  "description": "A friendly greeting template",
  "template_yaml": "prompt: Hello {{ name }}! Welcome to {{ service }}.",
  "variables": ["name", "service"],
  "is_active": true,
  "created_at": "2025-11-11T08:00:00",
  "updated_at": "2025-11-11T08:00:00"
}
```

### Versioning

When you create a template with the same name as an existing template, a new version is automatically created:

```bash
# Create version 1
curl -X POST "http://localhost:8000/prompts/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "greeting",
    "template_yaml": "prompt: Hello {{ name }}!"
  }'

# Create version 2 (same name)
curl -X POST "http://localhost:8000/prompts/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "greeting",
    "template_yaml": "prompt: Hi {{ name }}, welcome back!"
  }'
```

### Retrieving Templates

**Get latest version:**
```bash
curl "http://localhost:8000/prompts/by-name/greeting"
```

**Get specific version:**
```bash
curl "http://localhost:8000/prompts/by-name/greeting?version=1"
```

**Get by ID:**
```bash
curl "http://localhost:8000/prompts/1"
```

**List all templates:**
```bash
curl "http://localhost:8000/prompts/"
```

### Preview Templates

Preview how a template will render with specific variables:

```bash
curl -X POST "http://localhost:8000/prompts/preview" \
  -H "Content-Type: application/json" \
  -d '{
    "template_yaml": "Hello {{ name }}! Today is {{ day }}.",
    "variables": {
      "name": "Alice",
      "day": "Monday"
    }
  }'
```

**Response:**
```json
{
  "rendered": "Hello Alice! Today is Monday.",
  "original_yaml": "Hello {{ name }}! Today is {{ day }}.",
  "variables_used": {
    "name": "Alice",
    "day": "Monday"
  }
}
```

### Updating Templates

Update a specific template version (does not create a new version):

```bash
curl -X PUT "http://localhost:8000/prompts/1" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated description",
    "is_active": true
  }'
```

### Deleting Templates

Soft delete (marks as inactive):

```bash
curl -X DELETE "http://localhost:8000/prompts/1"
```

## Job Tracking

### Creating Jobs

Jobs can be associated with prompt templates to track which version was used:

```bash
curl -X POST "http://localhost:8000/jobs/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "analyze_data",
    "prompt_template_id": 1,
    "input_data": {
      "dataset": "sales_2025.csv"
    }
  }'
```

**Response:**
```json
{
  "id": 1,
  "name": "analyze_data",
  "prompt_template_id": 1,
  "prompt_version": 1,
  "status": "pending",
  "input_data": {
    "dataset": "sales_2025.csv"
  },
  "output_data": null,
  "created_at": "2025-11-11T08:00:00",
  "completed_at": null
}
```

**Note:** The `prompt_version` field automatically records which version of the template was used.

### Retrieving Jobs

**Get specific job:**
```bash
curl "http://localhost:8000/jobs/1"
```

**List all jobs:**
```bash
curl "http://localhost:8000/jobs/"
```

## YAML Template Examples

See the `examples/` directory for sample templates:

- `greeting_template.yaml` - Simple greeting with conditional content
- `code_review_template.yaml` - Code review assistant
- `data_analysis_template.yaml` - Data analysis helper

### Example Template Structure

```yaml
# System prompt for the AI
system_prompt: |
  You are an expert {{ role }}.

# User prompt with variables
user_prompt: |
  Please help me with {{ task }}.
  
  Context: {{ context }}

# Metadata
context:
  role: "{{ role }}"
  task_type: "{{ task_type }}"

# Parameters
parameters:
  temperature: 0.7
  max_tokens: 1000
```

## API Endpoints

### Prompt Templates

- `POST /prompts/` - Create a new prompt template
- `GET /prompts/` - List all prompt templates
- `GET /prompts/{template_id}` - Get a specific template by ID
- `GET /prompts/by-name/{name}` - Get template by name (with optional version)
- `PUT /prompts/{template_id}` - Update a template
- `DELETE /prompts/{template_id}` - Delete a template (soft delete)
- `POST /prompts/preview` - Preview template with variables

### Jobs

- `POST /jobs/` - Create a new job
- `GET /jobs/` - List all jobs
- `GET /jobs/{job_id}` - Get a specific job (includes prompt version used)

### System

- `GET /` - Root endpoint
- `GET /health` - Health check

## Testing

Run the test suite:

```bash
# Install test dependencies (already in requirements.txt)
pip install pytest pytest-asyncio httpx

# Run all tests
pytest

# Run with coverage
pytest --cov=aurea_orchestrator

# Run specific test file
pytest tests/test_api.py
```

## Development

### Project Structure

### Project Structure

```
aurea-orchestrator/
├── aurea_orchestrator/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py         # SQLAlchemy models
│   │   └── config.py           # Database configuration
│   ├── api/
│   │   ├── __init__.py
│   │   ├── schemas.py          # Pydantic schemas
│   │   ├── prompts.py          # Prompt endpoints
│   │   └── jobs.py             # Job endpoints
│   └── services/
│       ├── __init__.py
│       └── prompt_service.py   # Business logic
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_prompt_service.py
│   └── test_job_service.py
├── examples/
│   ├── greeting_template.yaml
│   ├── code_review_template.yaml
│   └── data_analysis_template.yaml
├── requirements.txt
└── README.md
```

### Database

The application uses SQLite by default. The database file `aurea_orchestrator.db` is created automatically on first run.

### Adding New Features

1. Update models in `aurea_orchestrator/models/database.py`
2. Add service methods in `aurea_orchestrator/services/`
3. Create API schemas in `aurea_orchestrator/api/schemas.py`
4. Add endpoints in `aurea_orchestrator/api/`
5. Write tests in `tests/`

## License

MIT

## Security Considerations

The Prompt Registry uses Jinja2 for template rendering, which allows dynamic content generation. Please note:

- **Template Injection**: The system is designed to allow trusted users to create and manage templates. If you expose the API publicly, implement proper authentication and authorization.
- **Input Validation**: All templates are validated for YAML syntax and Jinja2 template syntax before being stored.
- **Sandboxing**: Consider implementing additional sandboxing measures if templates come from untrusted sources.
- **Access Control**: Implement role-based access control (RBAC) for production deployments.

**Recommendation**: Use this system in controlled environments where template creators are trusted users.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
