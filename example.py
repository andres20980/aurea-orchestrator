#!/usr/bin/env python3
"""
Example demonstration of Review Agent with Job Status integration
"""

from job_status import JobState, JobStatus
from review_agent import ReviewAgent


def main():
    # Create a job
    job = JobStatus(job_id="example-job-001", state=JobState.PENDING)
    print(f"Job created: {job.job_id}")
    print(f"Initial state: {job.state.value}\n")

    # Start the job
    job.update_state(JobState.RUNNING)
    print(f"Job started at: {job.updated_at}\n")

    # Run code review
    print("Running code review...")
    agent = ReviewAgent(project_path=".", coverage_threshold=70.0)
    review_result = agent.review()

    # Add review to job
    job.add_review(review_result)
    job.update_state(JobState.COMPLETED)

    # Display review summary
    print("\n" + job.get_review_summary())

    # Display job status as dict
    print("\nJob Status (JSON):")
    import json

    print(json.dumps(job.to_dict(), indent=2, default=str))


if __name__ == "__main__":
    main()
