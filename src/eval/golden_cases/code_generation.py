"""Golden test cases for code generation feature"""

GOLDEN_CASES = [
    {
        "case_id": "code_gen_001",
        "feature_type": "code_generation",
        "test_type": "golden",
        "description": "Generate a simple addition function",
        "input_data": {
            "prompt": "Create a Python function that adds two numbers"
        },
        "expected_output": {
            "contains": ["def", "add", "return", "+"]
        },
        "metadata": {
            "difficulty": "easy",
            "language": "python"
        }
    },
    {
        "case_id": "code_gen_002",
        "feature_type": "code_generation",
        "test_type": "golden",
        "description": "Generate a function with error handling",
        "input_data": {
            "prompt": "Create a Python function to divide two numbers with error handling for division by zero"
        },
        "expected_output": {
            "contains": ["def", "divide", "try", "except", "ZeroDivisionError"]
        },
        "metadata": {
            "difficulty": "medium",
            "language": "python"
        }
    },
    {
        "case_id": "code_gen_003",
        "feature_type": "code_generation",
        "test_type": "golden",
        "description": "Generate a class with methods",
        "input_data": {
            "prompt": "Create a Python class Calculator with add and subtract methods"
        },
        "expected_output": {
            "contains": ["class", "Calculator", "def add", "def subtract"]
        },
        "metadata": {
            "difficulty": "medium",
            "language": "python"
        }
    }
]
