"""
Aurea Client SDK - Python client for Aurea Orchestrator API
"""
from typing import Optional, Dict, Any
import requests
from datetime import datetime


class AureaClient:
    """
    Python client for interacting with the Aurea Orchestrator API.
    
    This client provides convenient methods for submitting orchestration requests,
    checking their status, and approving/rejecting requests.
    
    Example:
        >>> client = AureaClient(base_url="http://localhost:8000", api_key="your-api-key")
        >>> response = client.request("Analyze customer data", {"dataset": "customers.csv"})
        >>> print(response["request_id"])
    """
    
    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        """
        Initialize the Aurea client.
        
        Args:
            base_url: The base URL of the Aurea Orchestrator API (e.g., "http://localhost:8000")
            api_key: Your API key for authentication
            timeout: Request timeout in seconds (default: 30)
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            Response data as dictionary
            
        Raises:
            requests.HTTPError: If the request fails
        """
        url = f"{self.base_url}{endpoint}"
        kwargs.setdefault('timeout', self.timeout)
        
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        
        return response.json()
    
    def request(
        self,
        task_description: str,
        parameters: Optional[Dict[str, Any]] = None,
        priority: int = 1
    ) -> Dict[str, Any]:
        """
        Submit a new orchestration request.
        
        This method creates a new task request that will be queued for orchestration.
        The request will be in 'pending' status until it is approved.
        
        Args:
            task_description: Description of the task to orchestrate
            parameters: Optional dictionary of task parameters
            priority: Task priority from 1 (lowest) to 10 (highest), default is 1
            
        Returns:
            Dictionary containing:
                - request_id: Unique identifier for the request
                - status: Current status ('pending')
                - message: Response message
                - created_at: Timestamp when the request was created
                
        Example:
            >>> client = AureaClient("http://localhost:8000", "your-api-key")
            >>> response = client.request(
            ...     task_description="Process customer feedback",
            ...     parameters={"source": "surveys", "period": "2024-Q1"},
            ...     priority=5
            ... )
            >>> print(f"Request ID: {response['request_id']}")
        """
        payload = {
            "task_description": task_description,
            "parameters": parameters,
            "priority": priority
        }
        
        return self._make_request("POST", "/request", json=payload)
    
    def status(self, request_id: str) -> Dict[str, Any]:
        """
        Get the status of an orchestration request.
        
        This method retrieves the current status and details of a previously
        submitted request.
        
        Args:
            request_id: The unique identifier of the request
            
        Returns:
            Dictionary containing:
                - request_id: Unique identifier for the request
                - status: Current status (pending, approved, rejected, processing, completed, failed)
                - task_description: Description of the task
                - created_at: Timestamp when the request was created
                - updated_at: Timestamp of last update
                - result: Task result if completed (may be None)
                
        Example:
            >>> client = AureaClient("http://localhost:8000", "your-api-key")
            >>> status_info = client.status("550e8400-e29b-41d4-a716-446655440000")
            >>> print(f"Status: {status_info['status']}")
            >>> if status_info['result']:
            ...     print(f"Result: {status_info['result']}")
        """
        return self._make_request("GET", f"/status/{request_id}")
    
    def approve(
        self,
        request_id: str,
        approved: bool,
        comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Approve or reject an orchestration request.
        
        This method allows you to approve or reject a pending orchestration request.
        Approved requests will move to processing status.
        
        Args:
            request_id: The unique identifier of the request to approve/reject
            approved: True to approve, False to reject
            comment: Optional comment explaining the approval decision
            
        Returns:
            Dictionary containing:
                - request_id: Unique identifier for the request
                - status: Updated status (approved or rejected)
                - message: Response message
                
        Example:
            >>> client = AureaClient("http://localhost:8000", "your-api-key")
            >>> # Approve a request
            >>> response = client.approve(
            ...     request_id="550e8400-e29b-41d4-a716-446655440000",
            ...     approved=True,
            ...     comment="Approved for processing"
            ... )
            >>> print(response['message'])
            
            >>> # Reject a request
            >>> response = client.approve(
            ...     request_id="550e8400-e29b-41d4-a716-446655440000",
            ...     approved=False,
            ...     comment="Insufficient resources"
            ... )
        """
        payload = {
            "request_id": request_id,
            "approved": approved,
            "comment": comment
        }
        
        return self._make_request("POST", "/approve", json=payload)
    
    def close(self):
        """Close the HTTP session."""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


__version__ = "1.0.0"
__all__ = ["AureaClient"]
