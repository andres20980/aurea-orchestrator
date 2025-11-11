"""Main FastAPI application for Aurea Orchestrator"""

from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.database import init_db
from src.api import router as eval_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    init_db()
    yield


app = FastAPI(
    title="Aurea Orchestrator",
    description="Automated Unified Reasoning & Execution Agents - Evaluation System",
    version="0.1.0",
    lifespan=lifespan
)

# Include routers
app.include_router(eval_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Aurea Orchestrator",
        "version": "0.1.0",
        "description": "Agent Evaluation System",
        "endpoints": {
            "eval": "/eval/run - Run evaluation suite",
            "runs": "/eval/runs - List evaluation runs",
            "docs": "/docs - Interactive API documentation"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
