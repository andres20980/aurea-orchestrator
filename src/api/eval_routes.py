"""API routes for evaluation endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..database.models import EvalRun as EvalRunDB, EvalResult as EvalResultDB
from ..models.eval_models import (
    EvalRunRequest,
    EvalRunResponse,
    EvalResultResponse,
    FeatureType
)
from ..eval.runner import EvalRunner

router = APIRouter(prefix="/eval", tags=["evaluation"])


@router.post("/run", response_model=EvalRunResponse)
async def run_evaluation(
    request: EvalRunRequest,
    db: Session = Depends(get_db)
):
    """
    Trigger an evaluation suite.
    
    This endpoint runs evaluation tests based on the provided filters
    and returns the results with scorecard metrics.
    
    - **feature_type**: Filter by specific feature type (optional)
    - **test_type**: Filter by test type - "golden" or "regression" (optional)
    - **metadata**: Additional metadata to attach to this run (optional)
    """
    try:
        runner = EvalRunner(db)
        eval_run = runner.run_evaluation(
            feature_type=request.feature_type,
            test_type=request.test_type,
            metadata=request.metadata
        )
        
        # Convert to response model
        return _eval_run_to_response(eval_run)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@router.get("/runs", response_model=List[EvalRunResponse])
async def list_runs(
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    List recent evaluation runs.
    
    - **limit**: Maximum number of runs to return (default: 10)
    - **offset**: Number of runs to skip (default: 0)
    """
    runs = db.query(EvalRunDB).order_by(
        EvalRunDB.started_at.desc()
    ).limit(limit).offset(offset).all()
    
    return [_eval_run_to_response(run) for run in runs]


@router.get("/runs/{run_id}", response_model=EvalRunResponse)
async def get_run(
    run_id: str,
    include_results: bool = True,
    db: Session = Depends(get_db)
):
    """
    Get details of a specific evaluation run.
    
    - **run_id**: Unique identifier of the evaluation run
    - **include_results**: Whether to include individual test results (default: true)
    """
    run = db.query(EvalRunDB).filter(EvalRunDB.run_id == run_id).first()
    
    if not run:
        raise HTTPException(status_code=404, detail="Evaluation run not found")
    
    return _eval_run_to_response(run, include_results=include_results)


@router.get("/results/{run_id}", response_model=List[EvalResultResponse])
async def get_results(
    run_id: str,
    db: Session = Depends(get_db)
):
    """
    Get individual test results for a specific run.
    
    - **run_id**: Unique identifier of the evaluation run
    """
    run = db.query(EvalRunDB).filter(EvalRunDB.run_id == run_id).first()
    
    if not run:
        raise HTTPException(status_code=404, detail="Evaluation run not found")
    
    results = db.query(EvalResultDB).filter(
        EvalResultDB.run_id == run.id
    ).all()
    
    return [_eval_result_to_response(r) for r in results]


def _eval_run_to_response(
    run: EvalRunDB,
    include_results: bool = False
) -> EvalRunResponse:
    """Convert database EvalRun to response model"""
    results = None
    if include_results and run.results:
        results = [_eval_result_to_response(r) for r in run.results]
    
    return EvalRunResponse(
        run_id=run.run_id,
        status=run.status.value,
        feature_type=run.feature_type,
        started_at=run.started_at,
        completed_at=run.completed_at,
        total_cases=run.total_cases,
        passed_cases=run.passed_cases,
        failed_cases=run.failed_cases,
        average_accuracy=run.average_accuracy,
        average_latency=run.average_latency,
        total_cost=run.total_cost,
        results=results
    )


def _eval_result_to_response(result: EvalResultDB) -> EvalResultResponse:
    """Convert database EvalResult to response model"""
    return EvalResultResponse(
        case_id=result.case_id,
        feature_type=result.feature_type,
        test_type=result.test_type,
        passed=bool(result.passed),
        accuracy=result.accuracy,
        latency_ms=result.latency_ms,
        cost=result.cost,
        error_message=result.error_message,
        executed_at=result.executed_at
    )
