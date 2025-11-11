from typing import Dict, List
from datetime import datetime
from models import JobStatus, NodeStatus, WorkflowState, NodeProgress, JobStatusResponse
import uuid


class JobStore:
    """In-memory storage for job states"""
    
    def __init__(self):
        self.jobs: Dict[str, dict] = {}
    
    def create_job(self, input_data: dict, max_iterations: int = 3) -> str:
        """Create a new job and return its ID"""
        job_id = str(uuid.uuid4())
        now = datetime.now()
        
        self.jobs[job_id] = {
            "job_id": job_id,
            "status": JobStatus.PENDING,
            "created_at": now,
            "updated_at": now,
            "state": {
                "job_id": job_id,
                "input_data": input_data,
                "plan_output": None,
                "implement_output": None,
                "test_output": None,
                "review_precheck_output": None,
                "review_output": None,
                "review_decision": "pending",
                "iteration_count": 0,
                "max_iterations": max_iterations,
                "node_progress": [],
                "current_node": None,
                "error": None,
            }
        }
        
        return job_id
    
    def get_job(self, job_id: str) -> dict:
        """Get job by ID"""
        return self.jobs.get(job_id)
    
    def update_job_status(self, job_id: str, status: JobStatus):
        """Update overall job status"""
        if job_id in self.jobs:
            self.jobs[job_id]["status"] = status
            self.jobs[job_id]["updated_at"] = datetime.now()
    
    def update_job_state(self, job_id: str, state: WorkflowState):
        """Update job state"""
        if job_id in self.jobs:
            self.jobs[job_id]["state"] = state
            self.jobs[job_id]["updated_at"] = datetime.now()
    
    def add_node_progress(self, job_id: str, node_name: str, status: NodeStatus, 
                          output: str = None, error: str = None):
        """Add or update node progress"""
        if job_id not in self.jobs:
            return
        
        now = datetime.now()
        state = self.jobs[job_id]["state"]
        node_progress = state["node_progress"]
        
        # Find existing progress entry for this node
        existing_entry = None
        for entry in node_progress:
            if entry["node_name"] == node_name and entry["status"] != NodeStatus.COMPLETED:
                existing_entry = entry
                break
        
        if existing_entry:
            existing_entry["status"] = status
            if status == NodeStatus.RUNNING and not existing_entry.get("start_time"):
                existing_entry["start_time"] = now
            if status in [NodeStatus.COMPLETED, NodeStatus.FAILED]:
                existing_entry["end_time"] = now
            if output:
                existing_entry["output"] = output
            if error:
                existing_entry["error"] = error
        else:
            # Create new entry
            new_entry: NodeProgress = {
                "node_name": node_name,
                "status": status,
                "start_time": now if status == NodeStatus.RUNNING else None,
                "end_time": now if status in [NodeStatus.COMPLETED, NodeStatus.FAILED] else None,
                "output": output,
                "error": error,
            }
            node_progress.append(new_entry)
        
        self.jobs[job_id]["updated_at"] = datetime.now()
    
    def get_job_status(self, job_id: str) -> JobStatusResponse:
        """Get formatted job status"""
        job = self.get_job(job_id)
        if not job:
            return None
        
        state = job["state"]
        return JobStatusResponse(
            job_id=job_id,
            status=job["status"],
            current_node=state["current_node"],
            iteration_count=state["iteration_count"],
            max_iterations=state["max_iterations"],
            node_progress=state["node_progress"],
            created_at=job["created_at"],
            updated_at=job["updated_at"],
        )


# Global job store instance
job_store = JobStore()
