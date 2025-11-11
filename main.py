"""
Aurea Orchestrator - Main Application
Automated Unified Reasoning & Execution Agents with Telemetry
"""
import time
import random
from contextlib import asynccontextmanager
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor


# Pydantic Models
class Task(BaseModel):
    """Task model for orchestration"""
    id: str
    description: str
    llm_model: str = Field(default="gpt-4", description="LLM model to use")
    max_tokens: int = Field(default=1000, description="Maximum tokens for the task")
    
class TaskResult(BaseModel):
    """Task result model"""
    task_id: str
    status: str
    result: str
    tokens_used: int
    cost_usd: float
    latency_ms: float

class MetricsResponse(BaseModel):
    """Metrics summary response"""
    total_requests: int
    total_tasks_processed: int
    total_tokens_used: int
    total_cost_usd: float
    avg_latency_ms: float


# Prometheus Metrics
request_counter = Counter(
    'aurea_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_latency = Histogram(
    'aurea_request_latency_seconds',
    'Request latency in seconds',
    ['endpoint']
)

task_counter = Counter(
    'aurea_tasks_total',
    'Total tasks processed',
    ['model', 'status']
)

token_usage = Counter(
    'aurea_llm_tokens_total',
    'Total LLM tokens used',
    ['model']
)

task_cost = Counter(
    'aurea_llm_cost_usd_total',
    'Total LLM cost in USD',
    ['model']
)

active_tasks = Gauge(
    'aurea_active_tasks',
    'Number of currently active tasks'
)


# In-memory storage for demo
tasks_db: Dict[str, TaskResult] = {}
metrics_summary = {
    'total_requests': 0,
    'total_tasks_processed': 0,
    'total_tokens_used': 0,
    'total_cost_usd': 0.0,
    'latency_samples': []
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    # Startup
    print("🚀 Aurea Orchestrator starting up...")
    print("📊 Telemetry and monitoring enabled")
    yield
    # Shutdown
    print("👋 Aurea Orchestrator shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Aurea Orchestrator",
    description="Automated Unified Reasoning & Execution Agents with Telemetry",
    version="1.0.0",
    lifespan=lifespan
)


# Configure OpenTelemetry
prometheus_reader = PrometheusMetricReader()
provider = MeterProvider(metric_readers=[prometheus_reader])
metrics.set_meter_provider(provider)

# Instrument FastAPI
FastAPIInstrumentor.instrument_app(app)


# Simulate LLM cost calculation
def calculate_llm_cost(model: str, tokens: int) -> float:
    """Calculate estimated cost based on model and tokens"""
    cost_per_1k_tokens = {
        'gpt-4': 0.03,
        'gpt-3.5-turbo': 0.002,
        'claude-2': 0.025,
        'llama-2': 0.001
    }
    rate = cost_per_1k_tokens.get(model, 0.01)
    return (tokens / 1000.0) * rate


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Aurea Orchestrator",
        "version": "1.0.0",
        "status": "running",
        "features": ["telemetry", "monitoring", "opentelemetry", "prometheus"]
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/tasks", response_model=TaskResult)
async def create_task(task: Task):
    """
    Create and execute a new task
    Simulates LLM processing with metrics tracking
    """
    start_time = time.time()
    active_tasks.inc()
    
    try:
        # Simulate LLM processing
        processing_time = random.uniform(0.5, 3.0)  # 500ms to 3s
        time.sleep(processing_time)
        
        # Simulate token usage (random but realistic)
        tokens_used = random.randint(100, min(task.max_tokens, 2000))
        
        # Calculate cost
        cost = calculate_llm_cost(task.llm_model, tokens_used)
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        
        # Create result
        result = TaskResult(
            task_id=task.id,
            status="completed",
            result=f"Task '{task.description}' processed successfully using {task.llm_model}",
            tokens_used=tokens_used,
            cost_usd=round(cost, 6),
            latency_ms=round(latency_ms, 2)
        )
        
        # Store result
        tasks_db[task.id] = result
        
        # Update Prometheus metrics
        task_counter.labels(model=task.llm_model, status='completed').inc()
        token_usage.labels(model=task.llm_model).inc(tokens_used)
        task_cost.labels(model=task.llm_model).inc(cost)
        request_latency.labels(endpoint='/tasks').observe(time.time() - start_time)
        request_counter.labels(method='POST', endpoint='/tasks', status='200').inc()
        
        # Update summary metrics
        metrics_summary['total_tasks_processed'] += 1
        metrics_summary['total_tokens_used'] += tokens_used
        metrics_summary['total_cost_usd'] += cost
        metrics_summary['latency_samples'].append(latency_ms)
        
        return result
        
    except Exception as e:
        task_counter.labels(model=task.llm_model, status='failed').inc()
        request_counter.labels(method='POST', endpoint='/tasks', status='500').inc()
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        active_tasks.dec()


@app.get("/tasks/{task_id}", response_model=TaskResult)
async def get_task(task_id: str):
    """Get task result by ID"""
    start_time = time.time()
    
    if task_id not in tasks_db:
        request_counter.labels(method='GET', endpoint='/tasks/{task_id}', status='404').inc()
        raise HTTPException(status_code=404, detail="Task not found")
    
    request_latency.labels(endpoint='/tasks/{task_id}').observe(time.time() - start_time)
    request_counter.labels(method='GET', endpoint='/tasks/{task_id}', status='200').inc()
    
    return tasks_db[task_id]


@app.get("/tasks", response_model=List[TaskResult])
async def list_tasks():
    """List all tasks"""
    start_time = time.time()
    request_latency.labels(endpoint='/tasks').observe(time.time() - start_time)
    request_counter.labels(method='GET', endpoint='/tasks', status='200').inc()
    return list(tasks_db.values())


@app.get("/metrics/summary", response_model=MetricsResponse)
async def get_metrics_summary():
    """Get metrics summary"""
    avg_latency = (
        sum(metrics_summary['latency_samples']) / len(metrics_summary['latency_samples'])
        if metrics_summary['latency_samples'] else 0.0
    )
    
    return MetricsResponse(
        total_requests=metrics_summary['total_requests'],
        total_tasks_processed=metrics_summary['total_tasks_processed'],
        total_tokens_used=metrics_summary['total_tokens_used'],
        total_cost_usd=round(metrics_summary['total_cost_usd'], 6),
        avg_latency_ms=round(avg_latency, 2)
    )


@app.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint
    Returns metrics in Prometheus exposition format
    """
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
