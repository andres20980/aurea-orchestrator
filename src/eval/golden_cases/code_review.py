"""Golden test cases for code review feature"""

GOLDEN_CASES = [
    {
        "case_id": "code_review_001",
        "feature_type": "code_review",
        "test_type": "golden",
        "description": "Identify security vulnerability",
        "input_data": {
            "code": "import os\npassword = os.system('echo secret')\nprint(password)"
        },
        "expected_output": {
            "contains": ["security", "vulnerability", "avoid"]
        },
        "metadata": {
            "difficulty": "medium",
            "vulnerability_type": "command_injection"
        }
    },
    {
        "case_id": "code_review_002",
        "feature_type": "code_review",
        "test_type": "golden",
        "description": "Suggest code improvements",
        "input_data": {
            "code": "def calculate(a,b,c,d,e):\n    return a+b+c+d+e"
        },
        "expected_output": {
            "contains": ["parameters", "variable names", "improve"]
        },
        "metadata": {
            "difficulty": "easy"
        }
    }
]
