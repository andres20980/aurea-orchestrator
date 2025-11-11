#!/usr/bin/env python3
"""Example: Submit a simple Python code execution."""

import requests
import json

API_URL = "http://localhost:8000"

# Example 1: Simple Hello World
print("Example 1: Simple Hello World")
response = requests.post(
    f"{API_URL}/run",
    json={
        "code": "print('Hello from the sandbox!')",
        "language": "python",
        "timeout": 30,
        "readonly": True,
    }
)
result = response.json()
print(f"Status: {response.status_code}")
print(f"Success: {result['success']}")
print(f"Output: {result['stdout']}")
print(f"Execution time: {result['execution_time']:.3f}s")
print("-" * 50)

# Example 2: Code with multiple operations
print("\nExample 2: Multiple operations")
code = """
import math

for i in range(5):
    print(f"Square root of {i}: {math.sqrt(i):.2f}")
"""
response = requests.post(
    f"{API_URL}/run",
    json={
        "code": code,
        "language": "python",
        "timeout": 30,
    }
)
result = response.json()
print(f"Output:\n{result['stdout']}")
print("-" * 50)

# Example 3: Code with timeout
print("\nExample 3: Timeout demonstration")
code = """
import time
print("Starting long operation...")
time.sleep(100)  # This will timeout
print("This won't print")
"""
response = requests.post(
    f"{API_URL}/run",
    json={
        "code": code,
        "language": "python",
        "timeout": 5,  # 5 second timeout
    }
)
result = response.json()
print(f"Timed out: {result['timed_out']}")
print(f"Execution time: {result['execution_time']:.3f}s")
print("-" * 50)

# Example 4: JavaScript execution
print("\nExample 4: JavaScript/Node.js")
response = requests.post(
    f"{API_URL}/run",
    json={
        "code": "console.log('Hello from Node.js!'); console.log('2 + 2 =', 2 + 2);",
        "language": "javascript",
        "timeout": 30,
    }
)
result = response.json()
print(f"Output:\n{result['stdout']}")
print("-" * 50)

# Example 5: Error handling
print("\nExample 5: Error handling")
code = """
print("Before error")
raise ValueError("This is a test error")
print("After error - won't execute")
"""
response = requests.post(
    f"{API_URL}/run",
    json={
        "code": code,
        "language": "python",
        "timeout": 30,
    }
)
result = response.json()
print(f"Success: {result['success']}")
print(f"Exit code: {result['exit_code']}")
print(f"Stdout:\n{result['stdout']}")
print(f"Stderr:\n{result['stderr']}")
