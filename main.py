"""
Aurea Orchestrator - Main Application
Automated Unified Reasoning & Execution Agents
"""
import os
import time
from typing import Dict

from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
import psycopg2
from psycopg2.extras import RealDictCursor
import redis
from google.cloud import secretmanager

app = FastAPI(
    title="Aurea Orchestrator",
    description="Automated Unified Reasoning & Execution Agents",
    version="1.0.0"
)

# Initialize clients
redis_client = None
db_pool = None
secret_client = None


def get_secret(secret_id: str, project_id: str) -> str:
    """Retrieve secret from Google Cloud Secret Manager."""
    global secret_client
    if not secret_client:
        secret_client = secretmanager.SecretManagerServiceClient()
    
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = secret_client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")


def init_redis():
    """Initialize Redis connection."""
    global redis_client
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))
    
    try:
        redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=True,
            socket_connect_timeout=5
        )
        redis_client.ping()
    except Exception as e:
        print(f"Warning: Redis connection failed: {e}")
        redis_client = None


def init_db():
    """Initialize database connection pool."""
    global db_pool
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "aurea")
    db_user = os.getenv("DB_USER", "postgres")
    
    # Try to get password from Secret Manager
    project_id = os.getenv("GCP_PROJECT_ID")
    if project_id:
        try:
            db_password = get_secret("db-password", project_id)
        except Exception:
            db_password = os.getenv("DB_PASSWORD", "postgres")
    else:
        db_password = os.getenv("DB_PASSWORD", "postgres")
    
    try:
        db_pool = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password,
            cursor_factory=RealDictCursor
        )
    except Exception as e:
        print(f"Warning: Database connection failed: {e}")
        db_pool = None


@app.on_event("startup")
async def startup_event():
    """Initialize connections on startup."""
    init_redis()
    init_db()


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up connections on shutdown."""
    global redis_client, db_pool
    
    if redis_client:
        redis_client.close()
    
    if db_pool:
        db_pool.close()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Aurea Orchestrator",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run."""
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {}
    }
    
    # Check Redis
    if redis_client:
        try:
            redis_client.ping()
            health_status["services"]["redis"] = "healthy"
        except Exception as e:
            health_status["services"]["redis"] = f"unhealthy: {str(e)}"
            health_status["status"] = "degraded"
    else:
        health_status["services"]["redis"] = "not configured"
    
    # Check Database
    if db_pool:
        try:
            with db_pool.cursor() as cur:
                cur.execute("SELECT 1")
            health_status["services"]["database"] = "healthy"
        except Exception as e:
            health_status["services"]["database"] = f"unhealthy: {str(e)}"
            health_status["status"] = "degraded"
    else:
        health_status["services"]["database"] = "not configured"
    
    status_code = 200 if health_status["status"] in ["healthy", "degraded"] else 503
    return JSONResponse(content=health_status, status_code=status_code)


@app.get("/metrics")
async def metrics():
    """Prometheus-compatible metrics endpoint."""
    metrics_data = []
    
    # Application metrics
    metrics_data.append(f"# HELP aurea_up Application running status")
    metrics_data.append(f"# TYPE aurea_up gauge")
    metrics_data.append(f"aurea_up 1")
    
    # Redis metrics
    if redis_client:
        try:
            info = redis_client.info()
            metrics_data.append(f"# HELP aurea_redis_connected Redis connection status")
            metrics_data.append(f"# TYPE aurea_redis_connected gauge")
            metrics_data.append(f"aurea_redis_connected 1")
            
            metrics_data.append(f"# HELP aurea_redis_used_memory_bytes Redis memory usage")
            metrics_data.append(f"# TYPE aurea_redis_used_memory_bytes gauge")
            metrics_data.append(f"aurea_redis_used_memory_bytes {info.get('used_memory', 0)}")
        except Exception:
            metrics_data.append(f"aurea_redis_connected 0")
    
    # Database metrics
    if db_pool:
        try:
            with db_pool.cursor() as cur:
                cur.execute("SELECT COUNT(*) as count FROM pg_stat_activity")
                result = cur.fetchone()
                
                metrics_data.append(f"# HELP aurea_db_connected Database connection status")
                metrics_data.append(f"# TYPE aurea_db_connected gauge")
                metrics_data.append(f"aurea_db_connected 1")
                
                metrics_data.append(f"# HELP aurea_db_connections Database active connections")
                metrics_data.append(f"# TYPE aurea_db_connections gauge")
                metrics_data.append(f"aurea_db_connections {result['count']}")
        except Exception:
            metrics_data.append(f"aurea_db_connected 0")
    
    return Response(content="\n".join(metrics_data), media_type="text/plain")


@app.get("/api/v1/orchestrate")
async def orchestrate():
    """Main orchestration endpoint."""
    return {
        "message": "Orchestration endpoint - implementation pending",
        "status": "ok"
    }
