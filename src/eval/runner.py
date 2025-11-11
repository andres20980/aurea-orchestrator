"""Evaluation runner for executing test suites"""

import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from ..models.eval_models import FeatureType, EvalCase, EvalScore
from ..database.models import EvalRun, EvalResult, EvalStatus
from .scorecard import Scorecard
from .golden_cases import load_golden_cases, get_regression_cases


class MockAgent:
    """
    Mock agent for demonstration purposes.
    In production, this would be replaced with actual agent implementation.
    """
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent with given input.
        Returns mock output based on input.
        """
        # Simple mock: echo the prompt and add some expected keywords
        prompt = input_data.get("prompt", "")
        code = input_data.get("code", "")
        
        if "add" in prompt.lower():
            return {
                "code": "def add(a, b):\n    return a + b",
                "explanation": "Function to add two numbers"
            }
        elif "divide" in prompt.lower():
            return {
                "code": "def divide(a, b):\n    try:\n        return a / b\n    except ZeroDivisionError:\n        return None",
                "explanation": "Division with error handling"
            }
        elif "class" in prompt.lower() and "calculator" in prompt.lower():
            return {
                "code": "class Calculator:\n    def add(self, a, b):\n        return a + b\n    def subtract(self, a, b):\n        return a - b",
                "explanation": "Calculator class"
            }
        elif code:
            # Code review/debug scenarios
            return {
                "review": "Security vulnerability detected. Avoid using os.system with user input.",
                "suggestions": ["Use subprocess with proper sanitization", "Validate input"]
            }
        
        return {"output": "Generic response"}


class EvalRunner:
    """
    Runs evaluation suites and stores results in database.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.agent = MockAgent()  # Replace with actual agent in production
    
    def run_evaluation(
        self,
        feature_type: Optional[FeatureType] = None,
        test_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> EvalRun:
        """
        Run evaluation suite and store results.
        
        Args:
            feature_type: Filter by feature type (None for all)
            test_type: Filter by test type ("golden"/"regression", None for all)
            metadata: Additional metadata for this run
            
        Returns:
            EvalRun object with results
        """
        # Create eval run record
        run_id = str(uuid.uuid4())
        eval_run = EvalRun(
            run_id=run_id,
            status=EvalStatus.RUNNING,
            feature_type=feature_type.value if feature_type else None,
            started_at=datetime.utcnow(),
            metadata=metadata or {}
        )
        self.db.add(eval_run)
        self.db.commit()
        
        try:
            # Load test cases
            test_cases = self._load_test_cases(feature_type, test_type)
            
            # Execute each test case
            results = []
            total_accuracy = 0.0
            total_latency = 0.0
            total_cost = 0.0
            passed_count = 0
            
            for case_data in test_cases:
                result = self._execute_test_case(case_data, eval_run.id)
                results.append(result)
                
                if result.passed:
                    passed_count += 1
                if result.accuracy is not None:
                    total_accuracy += result.accuracy
                if result.latency_ms is not None:
                    total_latency += result.latency_ms
                if result.cost is not None:
                    total_cost += result.cost
            
            # Update run with results
            num_cases = len(results)
            eval_run.status = EvalStatus.COMPLETED
            eval_run.completed_at = datetime.utcnow()
            eval_run.total_cases = num_cases
            eval_run.passed_cases = passed_count
            eval_run.failed_cases = num_cases - passed_count
            eval_run.average_accuracy = total_accuracy / num_cases if num_cases > 0 else 0.0
            eval_run.average_latency = total_latency / num_cases if num_cases > 0 else 0.0
            eval_run.total_cost = total_cost
            
            self.db.commit()
            self.db.refresh(eval_run)
            
            return eval_run
            
        except Exception as e:
            # Mark run as failed
            eval_run.status = EvalStatus.FAILED
            eval_run.completed_at = datetime.utcnow()
            eval_run.metadata = {**(metadata or {}), "error": str(e)}
            self.db.commit()
            raise
    
    def _load_test_cases(
        self,
        feature_type: Optional[FeatureType],
        test_type: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Load test cases based on filters"""
        cases = []
        
        # Load golden cases
        if test_type is None or test_type == "golden":
            cases.extend(load_golden_cases(feature_type))
        
        # Load regression cases
        if test_type is None or test_type == "regression":
            cases.extend(get_regression_cases(feature_type))
        
        return cases
    
    def _execute_test_case(
        self,
        case_data: Dict[str, Any],
        run_id: int
    ) -> EvalResult:
        """Execute a single test case and return result"""
        scorecard = Scorecard()
        scorecard.start_timer()
        
        try:
            # Execute agent
            actual_output = self.agent.execute(case_data["input_data"])
            
            # Calculate metrics
            score = scorecard.evaluate(
                expected=case_data["expected_output"],
                actual=actual_output,
                input_tokens=100,  # Mock token counts
                output_tokens=50
            )
            
            # Create result record
            result = EvalResult(
                run_id=run_id,
                case_id=case_data["case_id"],
                feature_type=case_data["feature_type"],
                test_type=case_data["test_type"],
                input_data=case_data["input_data"],
                expected_output=case_data["expected_output"],
                actual_output=actual_output,
                passed=1 if score.passed else 0,
                accuracy=score.accuracy,
                latency_ms=score.latency_ms,
                cost=score.cost,
                executed_at=datetime.utcnow(),
                metadata=case_data.get("metadata")
            )
            
        except Exception as e:
            # Record failure
            result = EvalResult(
                run_id=run_id,
                case_id=case_data["case_id"],
                feature_type=case_data["feature_type"],
                test_type=case_data["test_type"],
                input_data=case_data["input_data"],
                expected_output=case_data["expected_output"],
                actual_output=None,
                passed=0,
                accuracy=0.0,
                latency_ms=scorecard.stop_timer(),
                cost=0.0,
                error_message=str(e),
                executed_at=datetime.utcnow(),
                metadata=case_data.get("metadata")
            )
        
        self.db.add(result)
        self.db.commit()
        
        return result
