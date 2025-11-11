"""Main FastAPI application"""

from fastapi import FastAPI
from aurea_orchestrator.models.config import init_db
from aurea_orchestrator.api.prompts import router as prompts_router
from aurea_orchestrator.api.jobs import router as jobs_router

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="Aurea Orchestrator",
    description="Automated Unified Reasoning & Execution Agents with Prompt Registry",
    version="0.1.0"
)

# Include routers
app.include_router(prompts_router)
app.include_router(jobs_router)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Aurea Orchestrator",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
