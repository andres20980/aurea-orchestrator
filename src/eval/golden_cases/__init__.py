"""Golden test cases loader"""

from typing import List, Dict, Any, Optional
from ...models.eval_models import FeatureType

# Import golden cases from feature modules
from .code_generation import GOLDEN_CASES as CODE_GEN_CASES
from .code_review import GOLDEN_CASES as CODE_REVIEW_CASES
from .debugging import GOLDEN_CASES as DEBUG_CASES


def load_golden_cases(
    feature_type: Optional[FeatureType] = None
) -> List[Dict[str, Any]]:
    """
    Load golden test cases, optionally filtered by feature type.
    
    Args:
        feature_type: Optional filter for specific feature type
        
    Returns:
        List of golden test cases
    """
    all_cases = CODE_GEN_CASES + CODE_REVIEW_CASES + DEBUG_CASES
    
    if feature_type is None:
        return all_cases
    
    return [
        case for case in all_cases 
        if case["feature_type"] == feature_type.value
    ]


def get_regression_cases(
    feature_type: Optional[FeatureType] = None
) -> List[Dict[str, Any]]:
    """
    Get regression test cases (subset of golden cases marked for regression).
    
    Args:
        feature_type: Optional filter for specific feature type
        
    Returns:
        List of regression test cases
    """
    golden_cases = load_golden_cases(feature_type)
    
    # For now, regression cases are a subset of golden cases
    # In production, you might load these from a separate source
    regression_cases = []
    for case in golden_cases:
        regression_case = case.copy()
        regression_case["test_type"] = "regression"
        regression_case["case_id"] = regression_case["case_id"].replace(
            case["feature_type"], 
            f"{case['feature_type']}_regression"
        )
        regression_cases.append(regression_case)
    
    return regression_cases
