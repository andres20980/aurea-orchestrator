# aurea-orchestrator
Automated Unified Reasoning & Execution Agents

## Overview

Aurea Orchestrator is a job orchestration system with built-in budget management capabilities. It allows organizations to run jobs while enforcing daily and monthly budget limits.

## Features

- **Per-Organization Budgets**: Set daily and monthly budget limits for each organization
- **Budget Enforcement Modes**:
  - **Soft Mode**: Warn when budget is exceeded but allow jobs to continue
  - **Hard Mode**: Stop jobs when budget limit is exceeded
- **Budget Dashboard**: Real-time visualization of budget usage and job statistics
- **Billing Summary**: Detailed billing reports with usage breakdowns
- **Environment Variable Configuration**: Configure default limits via environment variables
- **REST API**: Full API for programmatic access

## Setup

### Prerequisites

- Python 3.8+
- pip

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

3. Copy the example environment file:
```bash
cp .env.example .env
```

4. Edit `.env` to configure your settings:
```bash
# Default Budget Limits
DEFAULT_DAILY_BUDGET_LIMIT=1000.0
DEFAULT_MONTHLY_BUDGET_LIMIT=30000.0

# Budget Enforcement Mode (soft or hard)
DEFAULT_BUDGET_MODE=soft

# Database
DATABASE_URL=sqlite:///aurea.db
```

5. Initialize the database:
```bash
flask --app app init-db
```

6. (Optional) Seed sample data:
```bash
flask --app app seed-data
```

### Running the Application

```bash
python app.py
```

The application will be available at http://localhost:5000

## Usage

### Dashboard

Access the main dashboard at http://localhost:5000 to view:
- Real-time budget usage for selected organization
- Daily and monthly budget progress bars
- Job statistics
- Budget mode indicator

### Billing Summary

Access detailed billing information at http://localhost:5000/billing/summary

### API Endpoints

#### Organizations

- `GET /api/organizations` - List all organizations
- `POST /api/organizations` - Create a new organization
- `GET /api/organizations/<id>` - Get organization details
- `PUT /api/organizations/<id>` - Update organization
- `DELETE /api/organizations/<id>` - Delete organization

Example: Create an organization
```bash
curl -X POST http://localhost:5000/api/organizations \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Organization",
    "daily_budget_limit": 500.0,
    "monthly_budget_limit": 15000.0,
    "budget_mode": "soft"
  }'
```

#### Jobs

- `GET /api/jobs` - List all jobs (optional: ?organization_id=<id>)
- `POST /api/jobs` - Create a new job (checks budget)
- `POST /api/jobs/<id>/start` - Start a job (re-checks budget)
- `POST /api/jobs/<id>/complete` - Complete a job and record cost

Example: Create a job
```bash
curl -X POST http://localhost:5000/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "organization_id": 1,
    "name": "My Job",
    "estimated_cost": 25.0
  }'
```

Example: Complete a job
```bash
curl -X POST http://localhost:5000/api/jobs/1/complete \
  -H "Content-Type: application/json" \
  -d '{
    "cost": 30.0,
    "success": true
  }'
```

#### Billing

- `GET /api/billing/summary/<org_id>` - Get billing summary for an organization

Example:
```bash
curl http://localhost:5000/api/billing/summary/1
```

## Budget Enforcement

### Soft Mode
In soft mode, jobs will continue to run even if they exceed the budget limit. The system will warn you when limits are exceeded but will not block job execution.

### Hard Mode
In hard mode, jobs will be blocked from running if they would exceed the daily or monthly budget limit. Jobs that exceed the budget will have status `budget_exceeded`.

## Testing

Install test dependencies:
```bash
pip install -r requirements-dev.txt
```

Run tests:
```bash
pytest test_budget.py -v
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEFAULT_DAILY_BUDGET_LIMIT` | Default daily budget limit | 1000.0 |
| `DEFAULT_MONTHLY_BUDGET_LIMIT` | Default monthly budget limit | 30000.0 |
| `DEFAULT_BUDGET_MODE` | Default budget enforcement mode (soft/hard) | soft |
| `DATABASE_URL` | Database connection string | sqlite:///aurea.db |
| `SECRET_KEY` | Flask secret key | (change in production) |

## Architecture

### Models

- **Organization**: Represents an organization with budget settings
- **Budget**: Tracks daily/monthly budget usage per organization
- **Job**: Represents a job execution with associated cost

### Services

- **BudgetService**: Handles budget tracking, enforcement, and reporting

### API

Flask-based REST API with endpoints for organizations, jobs, and billing

### Dashboard

Web-based dashboard built with vanilla JavaScript and Flask templates
