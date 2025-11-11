"""
FastAPI application for Aurea Orchestrator with Model Router.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from app.router import ModelRouter

app = FastAPI(
    title="Aurea Orchestrator",
    description="Automated Unified Reasoning & Execution Agents with dynamic model routing",
    version="1.0.0"
)

# Initialize router
router = ModelRouter()


class ModelRequest(BaseModel):
    """Request to use a model."""
    model: Optional[str] = None  # If not specified, router will select
    prompt: str


class ModelResponse(BaseModel):
    """Response from model."""
    model: str
    response: str
    latency: float
    cost: float


class MetricsRecord(BaseModel):
    """Record metrics for a model request."""
    model: str
    latency: float
    cost: float
    success: bool


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Aurea Orchestrator",
        "status": "running",
        "endpoints": {
            "metrics": "/router/metrics",
            "optimize": "/router/optimize",
            "select": "/router/select",
            "weights": "/router/weights"
        }
    }


@app.get("/router/select")
async def select_model():
    """
    Select the best model based on current metrics and weights.
    
    Returns:
        Selected model and its score
    """
    model = router.select_model()
    score = router.calculate_model_score(model)
    
    return {
        "selected_model": model,
        "score": score,
        "weights": router.get_weights()
    }


@app.post("/router/record")
async def record_metrics(record: MetricsRecord):
    """
    Record metrics for a model request.
    
    Args:
        record: Metrics to record
        
    Returns:
        Confirmation
    """
    router.record_request(
        model=record.model,
        latency=record.latency,
        cost=record.cost,
        success=record.success
    )
    
    return {
        "status": "recorded",
        "model": record.model
    }


@app.get("/router/metrics")
async def get_metrics():
    """
    Get metrics summary for all models.
    
    Returns:
        Metrics for each model including:
        - Total requests
        - Success rate
        - Average latency
        - Average cost
        - Current score
    """
    return router.get_metrics_summary()


@app.post("/router/optimize")
async def optimize_weights():
    """
    Optimize selection weights based on recent performance.
    
    This endpoint should be called weekly to update weights.
    The optimization adjusts weights based on which metrics
    vary most across models (higher variance = more discriminating).
    
    Returns:
        Updated weights
    """
    new_weights = router.optimize_weights()
    
    return {
        "status": "optimized",
        "weights": new_weights,
        "metrics_summary": router.get_metrics_summary()
    }


@app.get("/router/weights")
async def get_weights():
    """
    Get current selection weights.
    
    Returns:
        Current weights for cost, quality, and latency
    """
    return router.get_weights()


@app.put("/router/weights")
async def update_weights(weights: Dict[str, float]):
    """
    Manually update selection weights.
    
    Args:
        weights: Dictionary with cost_weight, quality_weight, latency_weight
        
    Returns:
        Updated weights
    """
    total = sum(weights.values())
    if abs(total - 1.0) > 0.01:
        raise HTTPException(
            status_code=400,
            detail=f"Weights must sum to 1.0, got {total}"
        )
    
    if "cost_weight" in weights:
        router.weights.cost_weight = weights["cost_weight"]
    if "quality_weight" in weights:
        router.weights.quality_weight = weights["quality_weight"]
    if "latency_weight" in weights:
        router.weights.latency_weight = weights["latency_weight"]
    
    router._save_weights()
    
    return router.get_weights()
