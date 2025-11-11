"""
Job Status Module

Tracks job execution status and integrates review summaries.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from review_agent import ReviewResult


class JobState(Enum):
    """Job execution states"""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class JobStatus:
    """
    Job status with review summary integration.

    Tracks job execution and includes code review results.
    """

    job_id: str
    state: JobState
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    review_result: Optional[ReviewResult] = None
    messages: List[str] = field(default_factory=list)

    def update_state(self, new_state: JobState):
        """Update job state and timestamp"""
        self.state = new_state
        self.updated_at = datetime.now()

    def add_review(self, review_result: ReviewResult):
        """Add review result to job status"""
        self.review_result = review_result
        self.updated_at = datetime.now()

        # Add review summary to messages
        self.messages.append(f"Review Status: {review_result.status.value}")
        self.messages.append(review_result.summary)

    def to_dict(self) -> Dict:
        """Convert job status to dictionary"""
        result = {
            "job_id": self.job_id,
            "state": self.state.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "messages": self.messages,
        }

        if self.review_result:
            result["review"] = self.review_result.to_dict()

        return result

    def get_review_summary(self) -> str:
        """Get formatted review summary"""
        if not self.review_result:
            return "No review performed"

        lines = [
            "=" * 60,
            "CODE REVIEW SUMMARY",
            "=" * 60,
            f"Status: {self.review_result.status.value}",
            f"Coverage: {self.review_result.coverage_percentage or 'N/A'}%",
            f"Ruff: {'PASSED' if self.review_result.ruff_passed else 'FAILED'}",
            f"Black: {'PASSED' if self.review_result.black_passed else 'FAILED'}",
            f"Bandit HIGH Issues: {self.review_result.bandit_high_issues}",
            "-" * 60,
        ]

        for msg in self.review_result.messages:
            lines.append(f"  {msg}")

        lines.append("-" * 60)
        lines.append(self.review_result.summary)
        lines.append("=" * 60)

        return "\n".join(lines)
