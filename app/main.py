from fastapi import FastAPI
from app.core.database import engine, Base
from app.routers import auth, projects, jobs, metrics, costs

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Aurea Orchestrator",
    description="Automated Unified Reasoning & Execution Agents with project-level access controls",
    version="1.0.0"
)

# Include routers
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(jobs.router)
app.include_router(metrics.router)
app.include_router(costs.router)


@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "message": "Aurea Orchestrator API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy"}
