# aurea-orchestrator
Automated Unified Reasoning & Execution Agents

A modern orchestration platform with FastAPI backend and React dashboard for managing jobs, monitoring metrics, and reviewing results.

## Features

- **FastAPI Backend**: RESTful API with automatic OpenAPI documentation at `/docs`
- **React Dashboard**: Lightweight, modern UI built with Tailwind CSS and shadcn/ui
- **Job Management**: Track job status, progress, and results
- **Metrics Monitoring**: Real-time system and application metrics
- **Review System**: View and manage review results
- **Docker Support**: Fully containerized with docker-compose

## Quick Start

### Prerequisites

- Docker and Docker Compose (recommended)
- OR Python 3.11+ and Node.js 18+ (for local development)

### Using Docker Compose

1. **Start backend only:**
   ```bash
   docker-compose up
   ```
   Access the API at http://localhost:8000
   API documentation at http://localhost:8000/docs

2. **Start backend with dashboard:**
   ```bash
   docker-compose --profile dashboard up
   ```
   OR
   ```bash
   docker-compose --profile full up
   ```
   - API: http://localhost:8000
   - Dashboard: http://localhost:3000
   - API Docs: http://localhost:8000/docs

3. **Build and start in detached mode:**
   ```bash
   docker-compose --profile full up -d --build
   ```

4. **Stop services:**
   ```bash
   docker-compose down
   ```

### Local Development

#### Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

The API will be available at http://localhost:8000

#### Dashboard

```bash
cd dashboard
npm install
npm run dev
```

The dashboard will be available at http://localhost:5173 (Vite default port)

## API Endpoints

### Core Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)

### Jobs API

- `GET /api/jobs` - List all jobs
- `GET /api/jobs/{job_id}` - Get specific job details
- `POST /api/jobs` - Create a new job

### Metrics API

- `GET /api/metrics` - Get all metrics

### Reviews API

- `GET /api/reviews` - Get all reviews
- `GET /api/reviews/{job_id}` - Get reviews for a specific job

## Architecture

```
aurea-orchestrator/
├── backend/              # FastAPI backend
│   ├── main.py          # Main application
│   ├── requirements.txt # Python dependencies
│   └── Dockerfile       # Backend container
├── dashboard/           # React dashboard
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── lib/         # Utilities
│   │   └── App.jsx      # Main app
│   ├── Dockerfile       # Dashboard container
│   └── package.json     # Node dependencies
└── docker-compose.yml   # Container orchestration
```

## Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation

### Dashboard
- **React**: UI library
- **Vite**: Build tool
- **Tailwind CSS**: Utility-first CSS
- **shadcn/ui**: Component library
- **Lucide React**: Icon library

## Development

### Adding New Features

1. **Backend**: Add endpoints in `backend/main.py`
2. **Dashboard**: Add components in `dashboard/src/components/`
3. **Update Docker**: Rebuild containers with `docker-compose build`

### Environment Variables

#### Backend
- No environment variables required for basic setup
- Data is stored in-memory (use database in production)

#### Dashboard
- `VITE_API_URL`: Backend API URL (default: http://localhost:8000)

## Production Deployment

For production use:

1. Replace in-memory storage with a database (PostgreSQL, MongoDB, etc.)
2. Add authentication and authorization
3. Configure CORS properly in backend
4. Set up environment-specific configuration
5. Use proper secret management
6. Enable HTTPS/TLS
7. Configure monitoring and logging

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License
