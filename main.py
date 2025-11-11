"""
Aurea Orchestrator - Main Application
Automated Unified Reasoning & Execution Agents with Full Observability
"""
import logging
import uuid
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from observability import (
    setup_logging,
    setup_tracing,
    get_tracer,
    get_current_trace_id,
    get_trace_by_id,
    add_job_id_to_context
)


# Initialize logging first
logger = setup_logging()

# Define tracer
tracer = get_tracer(__name__)


class Job(BaseModel):
    """Job model for the orchestrator"""
    name: str
    description: Optional[str] = None
    parameters: Optional[dict] = None


class JobResponse(BaseModel):
    """Response model for job execution"""
    job_id: str
    status: str
    message: str
    trace_id: Optional[str] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for app startup and shutdown"""
    logger.info("Starting Aurea Orchestrator")
    yield
    logger.info("Shutting down Aurea Orchestrator")


# Initialize FastAPI app
app = FastAPI(
    title="Aurea Orchestrator",
    description="Automated Unified Reasoning & Execution Agents with Full Observability",
    version="1.0.0",
    lifespan=lifespan
)

# Setup OpenTelemetry tracing
setup_tracing(app)


@app.middleware("http")
async def add_trace_id_header(request: Request, call_next):
    """Middleware to add trace_id to response headers"""
    response = await call_next(request)
    trace_id = get_current_trace_id()
    if trace_id:
        response.headers["X-Trace-ID"] = trace_id
    return response


@app.get("/")
async def root():
    """Root endpoint"""
    with tracer.start_as_current_span("root_endpoint") as span:
        trace_id = get_current_trace_id()
        logger.info("Root endpoint accessed", extra={"trace_id": trace_id})
        return {
            "message": "Welcome to Aurea Orchestrator",
            "version": "1.0.0",
            "trace_id": trace_id
        }


@app.get("/health")
async def health():
    """Health check endpoint"""
    with tracer.start_as_current_span("health_check") as span:
        trace_id = get_current_trace_id()
        logger.info("Health check", extra={"trace_id": trace_id})
        return {
            "status": "healthy",
            "trace_id": trace_id
        }


@app.post("/jobs", response_model=JobResponse)
async def create_job(job: Job):
    """Create and execute a job"""
    job_id = str(uuid.uuid4())
    
    with tracer.start_as_current_span("create_job") as span:
        # Add job_id to logging context and span
        add_job_id_to_context(job_id)
        span.set_attribute("job.id", job_id)
        span.set_attribute("job.name", job.name)
        
        trace_id = get_current_trace_id()
        
        logger.info(
            f"Creating job: {job.name}",
            extra={
                "job_id": job_id,
                "trace_id": trace_id,
                "job_name": job.name
            }
        )
        
        # Simulate job execution
        with tracer.start_as_current_span("execute_job") as exec_span:
            exec_span.set_attribute("job.id", job_id)
            logger.info(
                f"Executing job: {job.name}",
                extra={
                    "job_id": job_id,
                    "trace_id": trace_id,
                    "job_name": job.name,
                    "parameters": job.parameters or {}
                }
            )
            
            # Simulate processing
            status = "completed"
            message = f"Job {job.name} executed successfully"
        
        logger.info(
            f"Job completed: {job.name}",
            extra={
                "job_id": job_id,
                "trace_id": trace_id,
                "status": status
            }
        )
        
        return JobResponse(
            job_id=job_id,
            status=status,
            message=message,
            trace_id=trace_id
        )


@app.get("/traces/{trace_id}")
async def get_trace(trace_id: str):
    """
    Get trace information by trace_id
    
    This endpoint returns information about a specific trace.
    The actual trace data is stored in Jaeger and can be viewed in the Jaeger UI.
    """
    with tracer.start_as_current_span("get_trace") as span:
        span.set_attribute("requested.trace_id", trace_id)
        current_trace_id = get_current_trace_id()
        
        logger.info(
            f"Retrieving trace information",
            extra={
                "trace_id": current_trace_id,
                "requested_trace_id": trace_id
            }
        )
        
        # Get trace information
        trace_info = get_trace_by_id(trace_id)
        
        if not trace_info:
            logger.warning(
                f"Trace not found",
                extra={
                    "trace_id": current_trace_id,
                    "requested_trace_id": trace_id
                }
            )
            raise HTTPException(
                status_code=404,
                detail=f"Trace {trace_id} not found or not available yet"
            )
        
        return {
            "trace_id": trace_id,
            "info": trace_info,
            "jaeger_ui": f"http://localhost:16686/trace/{trace_id}",
            "current_trace_id": current_trace_id
        }


@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    """Get job status by job_id"""
    with tracer.start_as_current_span("get_job") as span:
        add_job_id_to_context(job_id)
        span.set_attribute("job.id", job_id)
        
        trace_id = get_current_trace_id()
        
        logger.info(
            f"Retrieving job status",
            extra={
                "job_id": job_id,
                "trace_id": trace_id
            }
        )
        
        # In a real implementation, this would query a database
        return {
            "job_id": job_id,
            "status": "completed",
            "trace_id": trace_id,
            "message": "Job information retrieved"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=None  # Use our custom logging configuration
    )
