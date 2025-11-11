"""
Job Metadata Management
Stores and manages job execution metadata including agent versions
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import json
import os


class JobMetadata:
    """
    Manages metadata for orchestrator jobs, including agent versions used.
    """
    
    def __init__(self, job_id: str, job_type: str):
        """
        Initialize job metadata.
        
        Args:
            job_id: Unique identifier for the job
            job_type: Type of job being executed
        """
        self.job_id = job_id
        self.job_type = job_type
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.agent_versions: Dict[str, str] = {}
        self.status = 'initialized'
        self.results: List[Dict[str, Any]] = []
    
    def add_agent_version(self, agent_name: str, version: str):
        """
        Record the version of an agent used in this job.
        
        Args:
            agent_name: Name of the agent
            version: Version string of the agent
        """
        self.agent_versions[agent_name] = version
    
    def add_result(self, result: Dict[str, Any]):
        """
        Add a result to the job.
        
        Args:
            result: Result data from an agent execution
        """
        self.results.append({
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': result
        })
    
    def update_status(self, status: str):
        """
        Update the job status.
        
        Args:
            status: New status value
        """
        self.status = status
        self.updated_at = datetime.now(timezone.utc).isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert metadata to dictionary format.
        
        Returns:
            Dictionary representation of job metadata
        """
        return {
            'job_id': self.job_id,
            'job_type': self.job_type,
            'created_at': self.created_at,
            'updated_at': getattr(self, 'updated_at', self.created_at),
            'status': self.status,
            'agent_versions': self.agent_versions,
            'results': self.results
        }
    
    def to_json(self) -> str:
        """
        Convert metadata to JSON string.
        
        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'JobMetadata':
        """
        Create JobMetadata instance from dictionary.
        
        Args:
            data: Dictionary containing job metadata
            
        Returns:
            JobMetadata instance
        """
        metadata = cls(data['job_id'], data['job_type'])
        metadata.created_at = data['created_at']
        metadata.status = data['status']
        metadata.agent_versions = data['agent_versions']
        metadata.results = data['results']
        if 'updated_at' in data:
            metadata.updated_at = data['updated_at']
        return metadata


class JobMetadataStore:
    """
    Stores and retrieves job metadata.
    """
    
    def __init__(self, storage_dir: str = '.aurea/jobs'):
        """
        Initialize the metadata store.
        
        Args:
            storage_dir: Directory to store job metadata files
        """
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
    
    def save(self, metadata: JobMetadata):
        """
        Save job metadata to storage.
        
        Args:
            metadata: JobMetadata instance to save
        """
        filepath = os.path.join(self.storage_dir, f"{metadata.job_id}.json")
        with open(filepath, 'w') as f:
            f.write(metadata.to_json())
    
    def load(self, job_id: str) -> Optional[JobMetadata]:
        """
        Load job metadata from storage.
        
        Args:
            job_id: ID of the job to load
            
        Returns:
            JobMetadata instance or None if not found
        """
        filepath = os.path.join(self.storage_dir, f"{job_id}.json")
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        return JobMetadata.from_dict(data)
    
    def list_jobs(self) -> List[str]:
        """
        List all stored job IDs.
        
        Returns:
            List of job IDs
        """
        if not os.path.exists(self.storage_dir):
            return []
        
        return [
            filename[:-5]  # Remove .json extension
            for filename in os.listdir(self.storage_dir)
            if filename.endswith('.json')
        ]
    
    def compare_runs(self, job_id1: str, job_id2: str) -> Dict[str, Any]:
        """
        Compare agent versions between two job runs.
        
        Args:
            job_id1: First job ID
            job_id2: Second job ID
            
        Returns:
            Comparison results showing version differences
        """
        job1 = self.load(job_id1)
        job2 = self.load(job_id2)
        
        if not job1 or not job2:
            return {
                'error': 'One or both jobs not found',
                'job1_found': job1 is not None,
                'job2_found': job2 is not None
            }
        
        all_agents = set(job1.agent_versions.keys()) | set(job2.agent_versions.keys())
        
        differences = {}
        for agent in all_agents:
            v1 = job1.agent_versions.get(agent)
            v2 = job2.agent_versions.get(agent)
            
            if v1 != v2:
                differences[agent] = {
                    'job1_version': v1,
                    'job2_version': v2,
                    'changed': True
                }
            else:
                differences[agent] = {
                    'version': v1,
                    'changed': False
                }
        
        return {
            'job1': {
                'job_id': job1.job_id,
                'created_at': job1.created_at,
                'agent_versions': job1.agent_versions
            },
            'job2': {
                'job_id': job2.job_id,
                'created_at': job2.created_at,
                'agent_versions': job2.agent_versions
            },
            'differences': differences
        }
