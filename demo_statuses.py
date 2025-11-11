#!/usr/bin/env python3
"""
Demo script showing all three review statuses: APPROVED, NEEDS_REVISION, FAILED
"""

import tempfile
from pathlib import Path

from review_agent import ReviewAgent


def demo_approved():
    """Demonstrate APPROVED status with mock data"""
    print("=" * 70)
    print("DEMO 1: APPROVED Status")
    print("=" * 70)
    print("Running on current project (should pass all checks)...\n")

    agent = ReviewAgent(project_path=".", coverage_threshold=70.0)
    result = agent.review()

    print(f"Status: {result.status.value}")
    print(f"Coverage: {result.coverage_percentage}%")
    print(f"Ruff: {'PASSED' if result.ruff_passed else 'FAILED'}")
    print(f"Black: {'PASSED' if result.black_passed else 'FAILED'}")
    print(f"Bandit HIGH Issues: {result.bandit_high_issues}")
    print(f"\nSummary: {result.summary}\n")


def demo_needs_revision():
    """Demonstrate NEEDS_REVISION status (low coverage scenario)"""
    print("=" * 70)
    print("DEMO 2: NEEDS_REVISION Status (Low Coverage Scenario)")
    print("=" * 70)
    print("Simulating project with low coverage...\n")

    # Create temp directory with minimal code
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a simple Python file
        test_file = Path(tmpdir) / "sample.py"
        test_file.write_text(
            '''
def add(a, b):
    """Add two numbers"""
    return a + b

def subtract(a, b):
    """Subtract two numbers"""
    return a - b

def multiply(a, b):
    """Multiply two numbers"""
    return a * b
'''
        )

        # Create minimal test (won't cover all functions)
        test_file2 = Path(tmpdir) / "test_sample.py"
        test_file2.write_text(
            '''
from sample import add

def test_add():
    """Test only the add function"""
    assert add(2, 3) == 5
'''
        )

        agent = ReviewAgent(project_path=tmpdir, coverage_threshold=70.0)
        result = agent.review()

        print(f"Status: {result.status.value}")
        print(f"Coverage: {result.coverage_percentage}%")
        print(f"Ruff: {'PASSED' if result.ruff_passed else 'FAILED'}")
        print(f"Black: {'PASSED' if result.black_passed else 'FAILED'}")
        print(f"Bandit HIGH Issues: {result.bandit_high_issues}")
        print(f"\nSummary: {result.summary}\n")


def demo_failed():
    """Demonstrate FAILED status (security issues scenario)"""
    print("=" * 70)
    print("DEMO 3: FAILED Status (Security Issues Scenario)")
    print("=" * 70)
    print(
        "Note: This demo shows what WOULD happen with HIGH security issues.\n"
        "We won't actually create vulnerable code.\n"
    )

    # In real scenario, code with HIGH security issues would trigger FAILED
    print("Status: FAILED")
    print("Coverage: 85.0%")
    print("Ruff: PASSED")
    print("Black: PASSED")
    print("Bandit HIGH Issues: 2")
    print("\nSummary: Security issues found - code review FAILED")
    print("\nExample HIGH issues that would trigger FAILED status:")
    print("  - Use of eval() with user input")
    print("  - SQL injection vulnerabilities")
    print("  - Use of pickle with untrusted data")
    print("  - Hardcoded credentials\n")


def main():
    """Run all demos"""
    print("\n" + "=" * 70)
    print("REVIEW AGENT STATUS DEMONSTRATIONS")
    print("=" * 70 + "\n")

    demo_approved()
    demo_needs_revision()
    demo_failed()

    print("=" * 70)
    print("All demos complete!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
