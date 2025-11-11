"""FastAPI application for sandbox code execution."""

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uuid
import docker
from typing import Dict, Optional
import os

from .schemas import TestRunSpec, TestRunResult, HealthResponse
from .runner import SandboxRunner


# Global sandbox runner instance
sandbox_runner: Optional[SandboxRunner] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan (startup and shutdown)."""
    global sandbox_runner
    
    # Startup
    image = os.getenv("SANDBOX_IMAGE", "aurea-sandbox:latest")
    cpu_limit = float(os.getenv("SANDBOX_CPU_LIMIT", "1.0"))
    memory_limit = os.getenv("SANDBOX_MEMORY_LIMIT", "512m")
    default_timeout = int(os.getenv("SANDBOX_DEFAULT_TIMEOUT", "30"))
    
    sandbox_runner = SandboxRunner(
        image=image,
        cpu_limit=cpu_limit,
        memory_limit=memory_limit,
        default_timeout=default_timeout,
    )
    
    print(f"Sandbox runner initialized with image: {image}")
    
    yield
    
    # Shutdown
    if sandbox_runner:
        sandbox_runner.cleanup()


app = FastAPI(
    title="Aurea Sandbox Orchestrator",
    description="Isolated Docker runner for secure code execution with resource limits",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Aurea Sandbox Orchestrator",
        "version": "1.0.0",
        "description": "Isolated Docker runner for secure code execution",
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        client = docker.from_env()
        docker_info = client.version()
        docker_available = True
        docker_version = docker_info.get("Version", "unknown")
    except Exception as e:
        docker_available = False
        docker_version = None
    
    return HealthResponse(
        status="healthy" if docker_available else "degraded",
        sandbox_available=docker_available,
        docker_version=docker_version,
    )


@app.post("/run", response_model=TestRunResult, status_code=status.HTTP_200_OK)
async def submit_run(spec: TestRunSpec):
    """
    Submit a test run specification for execution in the sandbox.
    
    Args:
        spec: Test run specification including code, language, and options
        
    Returns:
        TestRunResult with execution output, logs, and artifacts
        
    Raises:
        HTTPException: If sandbox is not available or execution fails
    """
    if not sandbox_runner:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Sandbox runner not initialized",
        )
    
    # Generate unique run ID
    run_id = str(uuid.uuid4())
    
    try:
        # Execute code in sandbox
        result = sandbox_runner.run(
            code=spec.code,
            language=spec.language,
            timeout=spec.timeout,
            files=spec.files,
            readonly=spec.readonly,
            capture_artifacts=spec.capture_artifacts,
        )
        
        # Add run ID to result
        return TestRunResult(
            run_id=run_id,
            **result
        )
        
    except docker.errors.ImageNotFound:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Sandbox image not found: {sandbox_runner.image}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Execution failed: {str(e)}",
        )


@app.post("/build-image", status_code=status.HTTP_200_OK)
async def build_sandbox_image():
    """
    Build the sandbox Docker image.
    
    This endpoint triggers a build of the sandbox Docker image using the Dockerfile
    in the repository root.
    
    Returns:
        Success message
        
    Raises:
        HTTPException: If build fails
    """
    if not sandbox_runner:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Sandbox runner not initialized",
        )
    
    try:
        dockerfile_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "Dockerfile"
        )
        
        if not os.path.exists(dockerfile_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dockerfile not found",
            )
        
        sandbox_runner.build_image(dockerfile_path)
        
        return {"message": f"Successfully built image: {sandbox_runner.image}"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Build failed: {str(e)}",
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
