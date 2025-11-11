#!/usr/bin/env python
"""Run all tests for the Aurea Orchestrator"""

import sys
import subprocess

def run_test_file(test_file):
    """Run a single test file"""
    print(f"\n{'='*60}")
    print(f"Running {test_file}")
    print('='*60)
    
    result = subprocess.run(
        [sys.executable, test_file],
        env={'PYTHONPATH': '.'},
        capture_output=False
    )
    
    return result.returncode == 0

def main():
    """Run all tests"""
    test_files = [
        'tests/test_evaluator.py',
        'tests/test_router.py',
    ]
    
    print("Aurea Orchestrator Test Suite")
    print("="*60)
    
    all_passed = True
    for test_file in test_files:
        if not run_test_file(test_file):
            all_passed = False
    
    print(f"\n{'='*60}")
    if all_passed:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
