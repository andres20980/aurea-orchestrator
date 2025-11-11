"""Unit tests for golden cases loader"""

import pytest
from src.eval.golden_cases import load_golden_cases, get_regression_cases
from src.models.eval_models import FeatureType


def test_load_all_golden_cases():
    """Test loading all golden cases"""
    cases = load_golden_cases()
    assert len(cases) > 0
    assert all(case["test_type"] == "golden" for case in cases)


def test_load_golden_cases_by_feature():
    """Test filtering golden cases by feature type"""
    code_gen_cases = load_golden_cases(FeatureType.CODE_GENERATION)
    assert len(code_gen_cases) > 0
    assert all(case["feature_type"] == "code_generation" for case in code_gen_cases)
    
    code_review_cases = load_golden_cases(FeatureType.CODE_REVIEW)
    assert len(code_review_cases) > 0
    assert all(case["feature_type"] == "code_review" for case in code_review_cases)


def test_golden_case_structure():
    """Test that golden cases have required fields"""
    cases = load_golden_cases()
    
    required_fields = [
        "case_id", "feature_type", "test_type", 
        "description", "input_data", "expected_output"
    ]
    
    for case in cases:
        for field in required_fields:
            assert field in case, f"Missing field {field} in case {case.get('case_id')}"


def test_get_regression_cases():
    """Test loading regression test cases"""
    regression_cases = get_regression_cases()
    assert len(regression_cases) > 0
    assert all(case["test_type"] == "regression" for case in regression_cases)


def test_regression_cases_by_feature():
    """Test filtering regression cases by feature type"""
    regression_cases = get_regression_cases(FeatureType.CODE_GENERATION)
    assert len(regression_cases) > 0
    assert all(case["feature_type"] == "code_generation" for case in regression_cases)
    assert all(case["test_type"] == "regression" for case in regression_cases)
