"""
Unit tests for Job Status Module
"""

from datetime import datetime


from job_status import JobState, JobStatus
from review_agent import ReviewResult, ReviewStatus


class TestJobStatus:
    """Test cases for JobStatus class"""

    def test_init(self):
        """Test JobStatus initialization"""
        status = JobStatus(job_id="test-job-1", state=JobState.PENDING)

        assert status.job_id == "test-job-1"
        assert status.state == JobState.PENDING
        assert isinstance(status.created_at, datetime)
        assert isinstance(status.updated_at, datetime)
        assert status.review_result is None
        assert status.messages == []

    def test_update_state(self):
        """Test state update"""
        status = JobStatus(job_id="test-job-1", state=JobState.PENDING)
        original_time = status.updated_at

        status.update_state(JobState.RUNNING)

        assert status.state == JobState.RUNNING
        assert status.updated_at > original_time

    def test_add_review(self):
        """Test adding review result"""
        status = JobStatus(job_id="test-job-1", state=JobState.COMPLETED)

        review = ReviewResult(
            status=ReviewStatus.APPROVED,
            coverage_percentage=85.5,
            ruff_passed=True,
            black_passed=True,
            bandit_high_issues=0,
            messages=["All checks passed"],
            summary="Code review approved",
        )

        status.add_review(review)

        assert status.review_result == review
        assert "Review Status: APPROVED" in status.messages
        assert "Code review approved" in status.messages

    def test_to_dict_without_review(self):
        """Test to_dict conversion without review"""
        status = JobStatus(job_id="test-job-1", state=JobState.RUNNING)
        status.messages.append("Job started")

        result = status.to_dict()

        assert result["job_id"] == "test-job-1"
        assert result["state"] == "RUNNING"
        assert "created_at" in result
        assert "updated_at" in result
        assert result["messages"] == ["Job started"]
        assert "review" not in result

    def test_to_dict_with_review(self):
        """Test to_dict conversion with review"""
        status = JobStatus(job_id="test-job-1", state=JobState.COMPLETED)

        review = ReviewResult(
            status=ReviewStatus.APPROVED,
            coverage_percentage=85.5,
            ruff_passed=True,
            black_passed=True,
            bandit_high_issues=0,
            messages=["All checks passed"],
            summary="Code review approved",
        )

        status.add_review(review)
        result = status.to_dict()

        assert "review" in result
        assert result["review"]["status"] == "APPROVED"
        assert result["review"]["coverage_percentage"] == 85.5

    def test_get_review_summary_no_review(self):
        """Test get_review_summary without review"""
        status = JobStatus(job_id="test-job-1", state=JobState.PENDING)

        summary = status.get_review_summary()

        assert summary == "No review performed"

    def test_get_review_summary_with_review(self):
        """Test get_review_summary with review"""
        status = JobStatus(job_id="test-job-1", state=JobState.COMPLETED)

        review = ReviewResult(
            status=ReviewStatus.APPROVED,
            coverage_percentage=85.5,
            ruff_passed=True,
            black_passed=True,
            bandit_high_issues=0,
            messages=["Coverage: 85.5%", "Ruff check: PASSED"],
            summary="All checks passed - code review APPROVED",
        )

        status.add_review(review)
        summary = status.get_review_summary()

        assert "CODE REVIEW SUMMARY" in summary
        assert "Status: APPROVED" in summary
        assert "Coverage: 85.5%" in summary
        assert "Ruff: PASSED" in summary
        assert "Black: PASSED" in summary
        assert "Bandit HIGH Issues: 0" in summary
        assert "All checks passed - code review APPROVED" in summary

    def test_get_review_summary_needs_revision(self):
        """Test get_review_summary with NEEDS_REVISION status"""
        status = JobStatus(job_id="test-job-1", state=JobState.COMPLETED)

        review = ReviewResult(
            status=ReviewStatus.NEEDS_REVISION,
            coverage_percentage=65.0,
            ruff_passed=True,
            black_passed=False,
            bandit_high_issues=0,
            messages=["Coverage: 65.0%", "Black check: FAILED"],
            summary="Coverage below threshold - NEEDS REVISION",
        )

        status.add_review(review)
        summary = status.get_review_summary()

        assert "Status: NEEDS_REVISION" in summary
        assert "Coverage: 65.0%" in summary
        assert "Black: FAILED" in summary

    def test_get_review_summary_failed(self):
        """Test get_review_summary with FAILED status"""
        status = JobStatus(job_id="test-job-1", state=JobState.COMPLETED)

        review = ReviewResult(
            status=ReviewStatus.FAILED,
            coverage_percentage=85.0,
            ruff_passed=True,
            black_passed=True,
            bandit_high_issues=2,
            messages=["Bandit check: FAILED (2 HIGH severity issues)"],
            summary="Security issues found - code review FAILED",
        )

        status.add_review(review)
        summary = status.get_review_summary()

        assert "Status: FAILED" in summary
        assert "Bandit HIGH Issues: 2" in summary
        assert "Security issues found" in summary


class TestJobState:
    """Test cases for JobState enum"""

    def test_job_state_values(self):
        """Test JobState enum values"""
        assert JobState.PENDING.value == "PENDING"
        assert JobState.RUNNING.value == "RUNNING"
        assert JobState.COMPLETED.value == "COMPLETED"
        assert JobState.FAILED.value == "FAILED"
