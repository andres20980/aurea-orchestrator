"""Golden test cases for debugging feature"""

GOLDEN_CASES = [
    {
        "case_id": "debug_001",
        "feature_type": "debugging",
        "test_type": "golden",
        "description": "Find syntax error",
        "input_data": {
            "code": "def hello()\n    print('Hello')",
            "error": "SyntaxError: invalid syntax"
        },
        "expected_output": {
            "contains": ["missing colon", ":", "def hello():"]
        },
        "metadata": {
            "difficulty": "easy",
            "error_type": "syntax"
        }
    },
    {
        "case_id": "debug_002",
        "feature_type": "debugging",
        "test_type": "golden",
        "description": "Fix logic error",
        "input_data": {
            "code": "def factorial(n):\n    if n == 0:\n        return 0\n    return n * factorial(n-1)",
            "issue": "Returns 0 for factorial of 0 instead of 1"
        },
        "expected_output": {
            "contains": ["return 1", "factorial(0)", "should be 1"]
        },
        "metadata": {
            "difficulty": "medium",
            "error_type": "logic"
        }
    }
]
