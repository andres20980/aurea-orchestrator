"""Export module for converting approved jobs to training data in JSONL format."""
import json
from typing import List
from .models import Job, TrainingExample


def job_to_training_example(job: Job) -> TrainingExample:
    """Convert a job to a training example.
    
    Args:
        job: The job to convert
        
    Returns:
        TrainingExample with prompt, solution, and feedback
        
    Raises:
        ValueError: If job is missing required fields
    """
    if not job.solution:
        raise ValueError(f"Job {job.id} has no solution")
    
    feedback = None
    if job.review_feedback:
        feedback = {
            "reviewer": job.review_feedback.reviewer,
            "rating": job.review_feedback.rating,
            "comments": job.review_feedback.comments,
            "approved": job.review_feedback.approved,
            "reviewed_at": job.review_feedback.reviewed_at.isoformat()
        }
    
    return TrainingExample(
        prompt=job.prompt,
        solution=job.solution,
        feedback=feedback
    )


def export_jobs_to_jsonl(jobs: List[Job]) -> str:
    """Export jobs to JSONL format for LLM fine-tuning.
    
    Each line in the output is a JSON object with:
    - prompt: The original task/question
    - solution: The approved solution
    - feedback: Optional review feedback (reviewer, rating, comments, etc.)
    
    Args:
        jobs: List of jobs to export
        
    Returns:
        String containing JSONL formatted data
    """
    lines = []
    
    for job in jobs:
        try:
            example = job_to_training_example(job)
            # Convert to dict and then to JSON string
            json_str = json.dumps(example.model_dump(), ensure_ascii=False)
            lines.append(json_str)
        except ValueError as e:
            # Skip jobs that can't be converted (e.g., missing solution)
            print(f"Skipping job: {e}")
            continue
    
    return "\n".join(lines)


def export_approved_jobs_to_jsonl(jobs: List[Job]) -> str:
    """Export only approved jobs to JSONL format.
    
    This is a convenience function that filters for approved jobs
    before exporting.
    
    Args:
        jobs: List of jobs (will be filtered for approved ones)
        
    Returns:
        String containing JSONL formatted data
    """
    from .models import JobStatus
    
    approved_jobs = [
        job for job in jobs
        if job.status == JobStatus.APPROVED and job.solution and job.review_feedback
    ]
    
    return export_jobs_to_jsonl(approved_jobs)
