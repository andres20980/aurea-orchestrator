#!/usr/bin/env python3
"""
Quick check script - runs all quality checks at once
"""

import sys

from review_agent import ReviewAgent


def main():
    """Run quick quality check"""
    print("\n🔍 Running Aurea Quality Check...\n")

    agent = ReviewAgent(project_path=".", coverage_threshold=70.0)
    result = agent.review()

    # Print messages
    for msg in result.messages:
        if "PASSED" in msg:
            print(f"✅ {msg}")
        elif "FAILED" in msg:
            print(f"❌ {msg}")
        else:
            print(f"ℹ️  {msg}")

    print(f"\n{'='*60}")
    print(f"Result: {result.status.value}")
    print(f"{'='*60}\n")

    # Exit with appropriate code
    if result.status.value == "APPROVED":
        print("✨ All checks passed! Code is ready for merge.")
        sys.exit(0)
    elif result.status.value == "NEEDS_REVISION":
        print("⚠️  Code needs revision before merge.")
        sys.exit(1)
    else:  # FAILED
        print("🚨 Critical issues found! Review required.")
        sys.exit(2)


if __name__ == "__main__":
    main()
