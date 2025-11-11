from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

app = FastAPI(
    title="Aurea Orchestrator API",
    description="Automated Unified Reasoning & Execution Agents - API for managing jobs, metrics, and reviews",
    version="1.0.0",
)

# Configure CORS for dashboard access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Job(BaseModel):
    id: str
    name: str
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    progress: int = 0
    result: Optional[str] = None


class Metric(BaseModel):
    name: str
    value: float
    timestamp: datetime
    unit: str


class ReviewResult(BaseModel):
    id: str
    job_id: str
    reviewer: str
    score: float
    comments: str
    created_at: datetime


# In-memory storage (replace with database in production)
jobs_db = [
    Job(
        id="job-001",
        name="Data Processing Task",
        status=JobStatus.RUNNING,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        progress=45,
    ),
    Job(
        id="job-002",
        name="Model Training",
        status=JobStatus.COMPLETED,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        progress=100,
        result="Accuracy: 95.2%",
    ),
    Job(
        id="job-003",
        name="Report Generation",
        status=JobStatus.PENDING,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        progress=0,
    ),
]

metrics_db = [
    Metric(name="CPU Usage", value=65.5, timestamp=datetime.now(), unit="%"),
    Metric(name="Memory Usage", value=42.3, timestamp=datetime.now(), unit="%"),
    Metric(name="Active Jobs", value=5, timestamp=datetime.now(), unit="count"),
    Metric(name="Completed Jobs", value=123, timestamp=datetime.now(), unit="count"),
]

reviews_db = [
    ReviewResult(
        id="review-001",
        job_id="job-002",
        reviewer="AI Reviewer",
        score=4.5,
        comments="Excellent performance, minor optimizations possible",
        created_at=datetime.now(),
    ),
]


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Aurea Orchestrator API",
        "docs": "/docs",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now()}


@app.get("/api/jobs", response_model=List[Job])
async def get_jobs():
    """Get all jobs"""
    return jobs_db


@app.get("/api/jobs/{job_id}", response_model=Job)
async def get_job(job_id: str):
    """Get a specific job by ID"""
    for job in jobs_db:
        if job.id == job_id:
            return job
    raise HTTPException(status_code=404, detail="Job not found")


@app.post("/api/jobs", response_model=Job)
async def create_job(job: Job):
    """Create a new job"""
    jobs_db.append(job)
    return job


@app.get("/api/metrics", response_model=List[Metric])
async def get_metrics():
    """Get all metrics"""
    return metrics_db


@app.get("/api/reviews", response_model=List[ReviewResult])
async def get_reviews():
    """Get all review results"""
    return reviews_db


@app.get("/api/reviews/{job_id}", response_model=List[ReviewResult])
async def get_reviews_by_job(job_id: str):
    """Get review results for a specific job"""
    results = [r for r in reviews_db if r.job_id == job_id]
    if not results:
        raise HTTPException(status_code=404, detail="No reviews found for this job")
    return results


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
