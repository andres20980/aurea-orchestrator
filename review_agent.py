"""
Review Agent for Aurea Orchestrator

This module provides automated code review functionality that checks:
- Code coverage (≥70%)
- Code formatting (ruff and black)
- Security issues (Bandit - no HIGH severity issues)

Returns one of three statuses: APPROVED, NEEDS_REVISION, or FAILED
"""

import json
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional


class ReviewStatus(Enum):
    """Review status enumeration"""

    APPROVED = "APPROVED"
    NEEDS_REVISION = "NEEDS_REVISION"
    FAILED = "FAILED"


@dataclass
class ReviewResult:
    """Review result container"""

    status: ReviewStatus
    coverage_percentage: Optional[float]
    ruff_passed: bool
    black_passed: bool
    bandit_high_issues: int
    messages: List[str]
    summary: str

    def to_dict(self) -> Dict:
        """Convert review result to dictionary"""
        return {
            "status": self.status.value,
            "coverage_percentage": self.coverage_percentage,
            "ruff_passed": self.ruff_passed,
            "black_passed": self.black_passed,
            "bandit_high_issues": self.bandit_high_issues,
            "messages": self.messages,
            "summary": self.summary,
        }


class ReviewAgent:
    """
    Automated code review agent.

    Checks code quality metrics and returns review status.
    """

    def __init__(
        self,
        project_path: str = ".",
        coverage_threshold: float = 70.0,
        python_files_pattern: str = "**/*.py",
    ):
        """
        Initialize ReviewAgent.

        Args:
            project_path: Path to the project to review
            coverage_threshold: Minimum coverage percentage required (default: 70.0)
            python_files_pattern: Pattern for finding Python files (default: **/*.py)
        """
        self.project_path = Path(project_path).resolve()
        self.coverage_threshold = coverage_threshold
        self.python_files_pattern = python_files_pattern
        self.messages: List[str] = []

    def _run_command(
        self, cmd: List[str], check: bool = False
    ) -> subprocess.CompletedProcess:
        """
        Run a shell command and return the result.

        Args:
            cmd: Command and arguments as list
            check: Whether to raise exception on non-zero exit code

        Returns:
            CompletedProcess instance
        """
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                check=check,
            )
            return result
        except subprocess.CalledProcessError as e:
            return e

    def check_coverage(self) -> tuple[bool, Optional[float]]:
        """
        Check code coverage.

        Returns:
            Tuple of (passed: bool, coverage_percentage: float or None)
        """
        # Look for existing .coverage file or coverage report
        coverage_file = self.project_path / ".coverage"

        if not coverage_file.exists():
            # Try to run tests with coverage
            result = self._run_command(
                [sys.executable, "-m", "pytest", "--cov=.", "--cov-report=json"]
            )

        # Check for coverage.json
        coverage_json = self.project_path / "coverage.json"
        if coverage_json.exists():
            try:
                with open(coverage_json, "r") as f:
                    data = json.load(f)
                    coverage_pct = data.get("totals", {}).get("percent_covered", 0.0)
                    passed = coverage_pct >= self.coverage_threshold
                    msg = f"Coverage: {coverage_pct:.2f}% (threshold: {self.coverage_threshold}%)"
                    self.messages.append(msg)
                    return passed, coverage_pct
            except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
                msg = f"Coverage check failed: {e}"
                self.messages.append(msg)
                return False, None

        # Fallback: try coverage report command
        result = self._run_command(
            [sys.executable, "-m", "coverage", "report", "--format=total"]
        )

        if result.returncode == 0:
            try:
                coverage_pct = float(result.stdout.strip())
                passed = coverage_pct >= self.coverage_threshold
                msg = f"Coverage: {coverage_pct:.2f}% (threshold: {self.coverage_threshold}%)"
                self.messages.append(msg)
                return passed, coverage_pct
            except ValueError:
                pass

        # No coverage data available
        msg = "Coverage data not available - please run tests with coverage first"
        self.messages.append(msg)
        return False, None

    def check_ruff(self) -> bool:
        """
        Check code with ruff.

        Returns:
            True if ruff passes, False otherwise
        """
        # Find Python files
        python_files = list(self.project_path.glob(self.python_files_pattern))

        if not python_files:
            msg = "No Python files found to check with ruff"
            self.messages.append(msg)
            return True  # Pass if no files to check

        result = self._run_command([sys.executable, "-m", "ruff", "check", "."])

        if result.returncode == 0:
            self.messages.append("Ruff check: PASSED")
            return True
        else:
            self.messages.append(f"Ruff check: FAILED\n{result.stdout}")
            return False

    def check_black(self) -> bool:
        """
        Check code formatting with black.

        Returns:
            True if black check passes, False otherwise
        """
        # Find Python files
        python_files = list(self.project_path.glob(self.python_files_pattern))

        if not python_files:
            msg = "No Python files found to check with black"
            self.messages.append(msg)
            return True  # Pass if no files to check

        result = self._run_command(
            [sys.executable, "-m", "black", "--check", "--quiet", "."]
        )

        if result.returncode == 0:
            self.messages.append("Black check: PASSED")
            return True
        else:
            self.messages.append("Black check: FAILED - code needs formatting")
            return False

    def check_bandit(self) -> tuple[bool, int]:
        """
        Check for security issues with Bandit.

        Returns:
            Tuple of (passed: bool, high_issue_count: int)
        """
        # Find Python files
        python_files = list(self.project_path.glob(self.python_files_pattern))

        if not python_files:
            msg = "No Python files found to check with bandit"
            self.messages.append(msg)
            return True, 0  # Pass if no files to check

        result = self._run_command(
            [
                sys.executable,
                "-m",
                "bandit",
                "-r",
                ".",
                "-f",
                "json",
                "--severity-level",
                "high",
            ]
        )

        high_issues = 0
        try:
            # Bandit returns non-zero if issues found, but we still get JSON output
            output = result.stdout or result.stderr
            if output:
                data = json.loads(output)
                results = data.get("results", [])
                high_issues = len(
                    [r for r in results if r.get("issue_severity") == "HIGH"]
                )
        except (json.JSONDecodeError, KeyError):
            # If we can't parse, check stderr for issues
            if "No issues identified" in (result.stdout + result.stderr):
                high_issues = 0
            else:
                # Assume failure if we can't parse
                self.messages.append(
                    "Bandit check: Could not parse results, assuming issues exist"
                )
                return False, -1

        if high_issues == 0:
            self.messages.append("Bandit check: PASSED (no HIGH severity issues)")
            return True, 0
        else:
            self.messages.append(
                f"Bandit check: FAILED ({high_issues} HIGH severity issues found)"
            )
            return False, high_issues

    def review(self) -> ReviewResult:
        """
        Perform complete code review.

        Returns:
            ReviewResult with status and details
        """
        self.messages = []

        # Run all checks
        coverage_passed, coverage_pct = self.check_coverage()
        ruff_passed = self.check_ruff()
        black_passed = self.check_black()
        bandit_passed, bandit_high_issues = self.check_bandit()

        # Determine status
        critical_checks = [coverage_passed, ruff_passed, black_passed, bandit_passed]

        if all(critical_checks):
            status = ReviewStatus.APPROVED
            summary = "All checks passed - code review APPROVED"
        elif not bandit_passed:
            status = ReviewStatus.FAILED
            summary = "Security issues found - code review FAILED"
        elif not coverage_passed:
            status = ReviewStatus.NEEDS_REVISION
            summary = "Coverage below threshold - NEEDS REVISION"
        elif not ruff_passed or not black_passed:
            status = ReviewStatus.NEEDS_REVISION
            summary = "Code quality/formatting issues - NEEDS REVISION"
        else:
            status = ReviewStatus.NEEDS_REVISION
            summary = "Code review NEEDS REVISION"

        return ReviewResult(
            status=status,
            coverage_percentage=coverage_pct,
            ruff_passed=ruff_passed,
            black_passed=black_passed,
            bandit_high_issues=bandit_high_issues,
            messages=self.messages,
            summary=summary,
        )


def main():
    """CLI entry point for review agent"""
    import argparse

    parser = argparse.ArgumentParser(description="Aurea Review Agent")
    parser.add_argument(
        "--path", default=".", help="Path to project (default: current directory)"
    )
    parser.add_argument(
        "--coverage-threshold",
        type=float,
        default=70.0,
        help="Minimum coverage percentage (default: 70.0)",
    )
    parser.add_argument("--json", action="store_true", help="Output result as JSON")

    args = parser.parse_args()

    agent = ReviewAgent(
        project_path=args.path, coverage_threshold=args.coverage_threshold
    )
    result = agent.review()

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(f"\n{'='*60}")
        print("REVIEW SUMMARY")
        print(f"{'='*60}")
        for msg in result.messages:
            print(f"  {msg}")
        print(f"\n{result.summary}")
        print(f"Status: {result.status.value}")
        print(f"{'='*60}\n")

    # Exit with appropriate code
    sys.exit(0 if result.status == ReviewStatus.APPROVED else 1)


if __name__ == "__main__":
    main()
