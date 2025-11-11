"""In-memory storage for jobs (can be replaced with database later)."""
from typing import Dict, List, Optional
from .models import Job, JobStatus


class JobStorage:
    """Simple in-memory storage for jobs."""
    
    def __init__(self):
        self._jobs: Dict[str, Job] = {}
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize with some sample approved jobs for demonstration."""
        from datetime import datetime, timedelta
        from .models import ReviewFeedback
        
        sample_jobs = [
            Job(
                id="job-001",
                prompt="Write a Python function to reverse a string",
                solution="def reverse_string(s: str) -> str:\n    return s[::-1]",
                status=JobStatus.APPROVED,
                created_at=datetime.utcnow() - timedelta(days=2),
                completed_at=datetime.utcnow() - timedelta(days=1),
                review_feedback=ReviewFeedback(
                    reviewer="alice",
                    rating=5,
                    comments="Clean and efficient implementation",
                    approved=True
                )
            ),
            Job(
                id="job-002",
                prompt="Implement a function to check if a number is prime",
                solution="def is_prime(n: int) -> bool:\n    if n < 2:\n        return False\n    for i in range(2, int(n**0.5) + 1):\n        if n % i == 0:\n            return False\n    return True",
                status=JobStatus.APPROVED,
                created_at=datetime.utcnow() - timedelta(days=3),
                completed_at=datetime.utcnow() - timedelta(days=2),
                review_feedback=ReviewFeedback(
                    reviewer="bob",
                    rating=4,
                    comments="Good implementation with optimization",
                    approved=True
                )
            ),
            Job(
                id="job-003",
                prompt="Create a function to merge two sorted lists",
                solution="def merge_sorted_lists(list1: list, list2: list) -> list:\n    result = []\n    i, j = 0, 0\n    while i < len(list1) and j < len(list2):\n        if list1[i] <= list2[j]:\n            result.append(list1[i])\n            i += 1\n        else:\n            result.append(list2[j])\n            j += 1\n    result.extend(list1[i:])\n    result.extend(list2[j:])\n    return result",
                status=JobStatus.APPROVED,
                created_at=datetime.utcnow() - timedelta(days=1),
                completed_at=datetime.utcnow() - timedelta(hours=12),
                review_feedback=ReviewFeedback(
                    reviewer="alice",
                    rating=5,
                    comments="Excellent merge algorithm",
                    approved=True
                )
            ),
            Job(
                id="job-004",
                prompt="Write a function to calculate Fibonacci numbers",
                solution="def fibonacci(n: int) -> int:\n    if n <= 1:\n        return n\n    a, b = 0, 1\n    for _ in range(n - 1):\n        a, b = b, a + b\n    return b",
                status=JobStatus.COMPLETED,
                created_at=datetime.utcnow() - timedelta(hours=5),
                completed_at=datetime.utcnow() - timedelta(hours=3)
            ),
        ]
        
        for job in sample_jobs:
            self._jobs[job.id] = job
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get a job by ID."""
        return self._jobs.get(job_id)
    
    def get_all_jobs(self) -> List[Job]:
        """Get all jobs."""
        return list(self._jobs.values())
    
    def get_approved_jobs(self) -> List[Job]:
        """Get all approved jobs."""
        return [
            job for job in self._jobs.values()
            if job.status == JobStatus.APPROVED and job.review_feedback is not None
        ]
    
    def add_job(self, job: Job) -> Job:
        """Add a new job."""
        self._jobs[job.id] = job
        return job
    
    def update_job(self, job_id: str, job: Job) -> Optional[Job]:
        """Update an existing job."""
        if job_id in self._jobs:
            self._jobs[job_id] = job
            return job
        return None


# Global storage instance
storage = JobStorage()
