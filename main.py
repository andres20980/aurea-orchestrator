"""
FastAPI application for the Model Router with meta-learning capabilities.
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict
from database import Database
from router import ModelRouter
from visualization import generate_html_report
import uvicorn

app = FastAPI(
    title="Aurea Orchestrator - Model Router",
    description="Meta-learning system for intelligent model routing",
    version="1.0.0"
)

# Initialize database and router
db = Database()
router = ModelRouter(db)


class RouteRequest(BaseModel):
    """Request model for routing."""
    input_text: str


class FeedbackRequest(BaseModel):
    """Request model for submitting feedback."""
    input_text: str
    selected_model: str
    success: bool
    execution_time: Optional[float] = None
    confidence_score: Optional[float] = None
    features: Optional[Dict[str, float]] = None


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Aurea Orchestrator - Model Router API",
        "version": "1.0.0",
        "endpoints": {
            "/router/route": "Route input to appropriate model",
            "/router/feedback": "Submit feedback for a routing decision",
            "/router/retrain": "Retrain the router heuristic",
            "/router/metrics": "Get performance metrics",
            "/router/patterns": "Analyze success/fail patterns",
            "/router/visualize": "View performance visualizations"
        }
    }


@app.post("/router/route")
async def route_request(request: RouteRequest):
    """
    Route input text to the most appropriate model.
    
    Returns the selected model, confidence score, and extracted features.
    """
    try:
        selected_model, confidence, features = router.route(request.input_text)
        
        return {
            "selected_model": selected_model,
            "confidence_score": round(confidence, 3),
            "features": features,
            "available_models": router.available_models,
            "router_version": router.version
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Routing error: {str(e)}")


@app.post("/router/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """
    Submit feedback for a routing decision.
    
    This feedback is used to improve the router through meta-learning.
    """
    try:
        record = db.add_feedback(
            input_text=feedback.input_text,
            selected_model=feedback.selected_model,
            success=feedback.success,
            execution_time=feedback.execution_time,
            confidence_score=feedback.confidence_score,
            features=feedback.features
        )
        
        return {
            "status": "success",
            "feedback_id": record.id,
            "message": "Feedback recorded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feedback error: {str(e)}")


@app.post("/router/retrain")
async def retrain_router():
    """
    Retrain the router heuristic based on collected feedback.
    
    Analyzes success/failure patterns and updates routing weights.
    Returns metrics about the retraining process and accuracy improvements.
    """
    try:
        result = router.retrain()
        
        if result['status'] == 'insufficient_data':
            return JSONResponse(
                status_code=400,
                content=result
            )
        
        # Calculate accuracy gain
        accuracy_gain = 0.0
        metrics = db.get_all_metrics()
        if len(metrics) >= 2:
            accuracy_gain = (metrics[-1].accuracy - metrics[-2].accuracy) * 100
        
        return {
            "status": result['status'],
            "metrics": {
                "old_accuracy": round(result['old_accuracy'] * 100, 2),
                "accuracy_gain_percent": round(accuracy_gain, 2),
                "records_processed": result['records_processed'],
                "new_version": result['new_version']
            },
            "updated_weights": result['updated_weights'],
            "message": f"Router retrained successfully. Version upgraded to {result['new_version']}."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retraining error: {str(e)}")


@app.get("/router/metrics")
async def get_metrics():
    """
    Get current router performance metrics.
    """
    try:
        latest_metrics = db.get_latest_metrics()
        all_metrics = db.get_all_metrics()
        
        if not latest_metrics:
            return {
                "current_metrics": None,
                "history_count": 0,
                "message": "No metrics available yet"
            }
        
        return {
            "current_metrics": {
                "accuracy": round(latest_metrics.accuracy * 100, 2),
                "total_predictions": latest_metrics.total_predictions,
                "successful_predictions": latest_metrics.successful_predictions,
                "version": latest_metrics.version,
                "timestamp": latest_metrics.timestamp.isoformat()
            },
            "history_count": len(all_metrics),
            "all_metrics": [
                {
                    "accuracy": round(m.accuracy * 100, 2),
                    "total_predictions": m.total_predictions,
                    "successful_predictions": m.successful_predictions,
                    "version": m.version,
                    "timestamp": m.timestamp.isoformat()
                }
                for m in all_metrics
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metrics error: {str(e)}")


@app.get("/router/patterns")
async def analyze_patterns():
    """
    Analyze success/failure patterns from collected feedback.
    
    Returns detailed analysis of model performance and feature correlations.
    """
    try:
        patterns = router.analyze_patterns()
        
        return {
            "analysis": {
                "total_records": patterns['total_records'],
                "success_rate": round(patterns['success_rate'] * 100, 2),
                "successful_records": patterns.get('successful_records', 0)
            },
            "patterns": patterns['patterns']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pattern analysis error: {str(e)}")


@app.get("/router/visualize", response_class=HTMLResponse)
async def visualize_performance():
    """
    Generate and display performance visualizations.
    
    Returns an HTML page with charts showing accuracy improvements over time.
    """
    try:
        metrics = db.get_all_metrics()
        html_report = generate_html_report(metrics)
        return HTMLResponse(content=html_report)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Visualization error: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "router_version": router.version,
        "database_connected": True
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
