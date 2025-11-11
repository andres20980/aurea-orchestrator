"""
Unit tests for Review Agent
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch


from review_agent import ReviewAgent, ReviewResult, ReviewStatus


class TestReviewAgent:
    """Test cases for ReviewAgent class"""

    def test_init(self):
        """Test ReviewAgent initialization"""
        agent = ReviewAgent(project_path=".", coverage_threshold=80.0)
        assert agent.coverage_threshold == 80.0
        assert agent.project_path.is_absolute()

    def test_init_default_threshold(self):
        """Test ReviewAgent with default threshold"""
        agent = ReviewAgent()
        assert agent.coverage_threshold == 70.0

    @patch("review_agent.subprocess.run")
    def test_check_coverage_with_json_report(self, mock_run):
        """Test coverage check with JSON report"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create coverage.json file
            coverage_data = {"totals": {"percent_covered": 85.5}}
            coverage_file = Path(tmpdir) / "coverage.json"
            with open(coverage_file, "w") as f:
                json.dump(coverage_data, f)

            agent = ReviewAgent(project_path=tmpdir, coverage_threshold=70.0)
            passed, coverage_pct = agent.check_coverage()

            assert passed is True
            assert coverage_pct == 85.5
            assert any("Coverage: 85.5" in msg for msg in agent.messages)

    @patch("review_agent.subprocess.run")
    def test_check_coverage_below_threshold(self, mock_run):
        """Test coverage check below threshold"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create coverage.json file with low coverage
            coverage_data = {"totals": {"percent_covered": 65.0}}
            coverage_file = Path(tmpdir) / "coverage.json"
            with open(coverage_file, "w") as f:
                json.dump(coverage_data, f)

            agent = ReviewAgent(project_path=tmpdir, coverage_threshold=70.0)
            passed, coverage_pct = agent.check_coverage()

            assert passed is False
            assert coverage_pct == 65.0

    @patch("review_agent.subprocess.run")
    def test_check_coverage_no_data(self, mock_run):
        """Test coverage check with no data available"""
        with tempfile.TemporaryDirectory() as tmpdir:
            agent = ReviewAgent(project_path=tmpdir)

            # Mock subprocess to return error
            mock_run.return_value = Mock(returncode=1, stdout="", stderr="")

            passed, coverage_pct = agent.check_coverage()

            assert passed is False
            assert coverage_pct is None
            assert any("not available" in msg for msg in agent.messages)

    @patch("review_agent.subprocess.run")
    def test_check_ruff_pass(self, mock_run):
        """Test ruff check passing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a Python file
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("print('hello')\n")

            agent = ReviewAgent(project_path=tmpdir)

            # Mock successful ruff check
            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

            passed = agent.check_ruff()

            assert passed is True
            assert any("Ruff check: PASSED" in msg for msg in agent.messages)

    @patch("review_agent.subprocess.run")
    def test_check_ruff_fail(self, mock_run):
        """Test ruff check failing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a Python file
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("print('hello')\n")

            agent = ReviewAgent(project_path=tmpdir)

            # Mock failed ruff check
            mock_run.return_value = Mock(
                returncode=1, stdout="test.py:1:1: F401 imported but unused", stderr=""
            )

            passed = agent.check_ruff()

            assert passed is False
            assert any("Ruff check: FAILED" in msg for msg in agent.messages)

    @patch("review_agent.subprocess.run")
    def test_check_ruff_no_files(self, mock_run):
        """Test ruff check with no Python files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            agent = ReviewAgent(project_path=tmpdir)
            passed = agent.check_ruff()

            assert passed is True
            assert any("No Python files found" in msg for msg in agent.messages)

    @patch("review_agent.subprocess.run")
    def test_check_black_pass(self, mock_run):
        """Test black check passing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a Python file
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("print('hello')\n")

            agent = ReviewAgent(project_path=tmpdir)

            # Mock successful black check
            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

            passed = agent.check_black()

            assert passed is True
            assert any("Black check: PASSED" in msg for msg in agent.messages)

    @patch("review_agent.subprocess.run")
    def test_check_black_fail(self, mock_run):
        """Test black check failing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a Python file
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("print('hello')\n")

            agent = ReviewAgent(project_path=tmpdir)

            # Mock failed black check
            mock_run.return_value = Mock(
                returncode=1, stdout="would reformat test.py", stderr=""
            )

            passed = agent.check_black()

            assert passed is False
            assert any("Black check: FAILED" in msg for msg in agent.messages)

    @patch("review_agent.subprocess.run")
    def test_check_black_no_files(self, mock_run):
        """Test black check with no Python files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            agent = ReviewAgent(project_path=tmpdir)
            passed = agent.check_black()

            assert passed is True
            assert any("No Python files found" in msg for msg in agent.messages)

    @patch("review_agent.subprocess.run")
    def test_check_bandit_pass(self, mock_run):
        """Test bandit check with no HIGH issues"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a Python file
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("print('hello')\n")

            agent = ReviewAgent(project_path=tmpdir)

            # Mock successful bandit check
            bandit_output = {"results": []}
            mock_run.return_value = Mock(
                returncode=0, stdout=json.dumps(bandit_output), stderr=""
            )

            passed, high_issues = agent.check_bandit()

            assert passed is True
            assert high_issues == 0
            assert any("Bandit check: PASSED" in msg for msg in agent.messages)

    @patch("review_agent.subprocess.run")
    def test_check_bandit_high_issues(self, mock_run):
        """Test bandit check with HIGH issues"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a Python file
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("import pickle\n")

            agent = ReviewAgent(project_path=tmpdir)

            # Mock bandit check with HIGH issues
            bandit_output = {
                "results": [
                    {"issue_severity": "HIGH", "issue_text": "Use of insecure pickle"},
                    {"issue_severity": "HIGH", "issue_text": "Another issue"},
                ]
            }
            mock_run.return_value = Mock(
                returncode=1, stdout=json.dumps(bandit_output), stderr=""
            )

            passed, high_issues = agent.check_bandit()

            assert passed is False
            assert high_issues == 2
            assert any("FAILED (2 HIGH" in msg for msg in agent.messages)

    @patch("review_agent.subprocess.run")
    def test_check_bandit_no_files(self, mock_run):
        """Test bandit check with no Python files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            agent = ReviewAgent(project_path=tmpdir)
            passed, high_issues = agent.check_bandit()

            assert passed is True
            assert high_issues == 0
            assert any("No Python files found" in msg for msg in agent.messages)

    @patch.object(ReviewAgent, "check_coverage")
    @patch.object(ReviewAgent, "check_ruff")
    @patch.object(ReviewAgent, "check_black")
    @patch.object(ReviewAgent, "check_bandit")
    def test_review_approved(self, mock_bandit, mock_black, mock_ruff, mock_coverage):
        """Test complete review with APPROVED status"""
        # Mock all checks passing
        mock_coverage.return_value = (True, 85.0)
        mock_ruff.return_value = True
        mock_black.return_value = True
        mock_bandit.return_value = (True, 0)

        agent = ReviewAgent()
        result = agent.review()

        assert result.status == ReviewStatus.APPROVED
        assert result.coverage_percentage == 85.0
        assert result.ruff_passed is True
        assert result.black_passed is True
        assert result.bandit_high_issues == 0
        assert "APPROVED" in result.summary

    @patch.object(ReviewAgent, "check_coverage")
    @patch.object(ReviewAgent, "check_ruff")
    @patch.object(ReviewAgent, "check_black")
    @patch.object(ReviewAgent, "check_bandit")
    def test_review_needs_revision_coverage(
        self, mock_bandit, mock_black, mock_ruff, mock_coverage
    ):
        """Test review with NEEDS_REVISION due to low coverage"""
        # Mock coverage failing
        mock_coverage.return_value = (False, 65.0)
        mock_ruff.return_value = True
        mock_black.return_value = True
        mock_bandit.return_value = (True, 0)

        agent = ReviewAgent()
        result = agent.review()

        assert result.status == ReviewStatus.NEEDS_REVISION
        assert result.coverage_percentage == 65.0
        assert "Coverage below threshold" in result.summary

    @patch.object(ReviewAgent, "check_coverage")
    @patch.object(ReviewAgent, "check_ruff")
    @patch.object(ReviewAgent, "check_black")
    @patch.object(ReviewAgent, "check_bandit")
    def test_review_needs_revision_formatting(
        self, mock_bandit, mock_black, mock_ruff, mock_coverage
    ):
        """Test review with NEEDS_REVISION due to formatting issues"""
        # Mock black failing
        mock_coverage.return_value = (True, 85.0)
        mock_ruff.return_value = True
        mock_black.return_value = False
        mock_bandit.return_value = (True, 0)

        agent = ReviewAgent()
        result = agent.review()

        assert result.status == ReviewStatus.NEEDS_REVISION
        assert "Code quality/formatting issues" in result.summary

    @patch.object(ReviewAgent, "check_coverage")
    @patch.object(ReviewAgent, "check_ruff")
    @patch.object(ReviewAgent, "check_black")
    @patch.object(ReviewAgent, "check_bandit")
    def test_review_failed_security(
        self, mock_bandit, mock_black, mock_ruff, mock_coverage
    ):
        """Test review with FAILED status due to security issues"""
        # Mock bandit failing with HIGH issues
        mock_coverage.return_value = (True, 85.0)
        mock_ruff.return_value = True
        mock_black.return_value = True
        mock_bandit.return_value = (False, 3)

        agent = ReviewAgent()
        result = agent.review()

        assert result.status == ReviewStatus.FAILED
        assert result.bandit_high_issues == 3
        assert "Security issues" in result.summary

    def test_review_result_to_dict(self):
        """Test ReviewResult to_dict conversion"""
        result = ReviewResult(
            status=ReviewStatus.APPROVED,
            coverage_percentage=85.5,
            ruff_passed=True,
            black_passed=True,
            bandit_high_issues=0,
            messages=["Test message"],
            summary="All checks passed",
        )

        result_dict = result.to_dict()

        assert result_dict["status"] == "APPROVED"
        assert result_dict["coverage_percentage"] == 85.5
        assert result_dict["ruff_passed"] is True
        assert result_dict["black_passed"] is True
        assert result_dict["bandit_high_issues"] == 0
        assert result_dict["messages"] == ["Test message"]
        assert result_dict["summary"] == "All checks passed"


class TestReviewStatus:
    """Test cases for ReviewStatus enum"""

    def test_review_status_values(self):
        """Test ReviewStatus enum values"""
        assert ReviewStatus.APPROVED.value == "APPROVED"
        assert ReviewStatus.NEEDS_REVISION.value == "NEEDS_REVISION"
        assert ReviewStatus.FAILED.value == "FAILED"
