"""
Aurea Orchestrator - Main FastAPI application
"""
from fastapi import FastAPI, Header, HTTPException, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

app = FastAPI(
    title="Aurea Orchestrator API",
    description="Automated Unified Reasoning & Execution Agents Orchestrator",
    version="1.0.0",
)

# API Key authentication
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Mock API key for demo purposes
VALID_API_KEY = "aurea-demo-api-key-12345"

# In-memory storage for demo
requests_db: Dict[str, Dict[str, Any]] = {}


class RequestStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class OrchestrationRequest(BaseModel):
    task_description: str = Field(..., description="Description of the task to orchestrate")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Task parameters")
    priority: Optional[int] = Field(default=1, description="Task priority (1-10)")


class OrchestrationResponse(BaseModel):
    request_id: str = Field(..., description="Unique identifier for the request")
    status: RequestStatus = Field(..., description="Current status of the request")
    message: str = Field(..., description="Response message")
    created_at: datetime = Field(..., description="Request creation timestamp")


class StatusResponse(BaseModel):
    request_id: str = Field(..., description="Unique identifier for the request")
    status: RequestStatus = Field(..., description="Current status of the request")
    task_description: str = Field(..., description="Description of the task")
    created_at: datetime = Field(..., description="Request creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    result: Optional[Dict[str, Any]] = Field(default=None, description="Task result if completed")


class ApprovalRequest(BaseModel):
    request_id: str = Field(..., description="Unique identifier for the request to approve")
    approved: bool = Field(..., description="Whether to approve or reject the request")
    comment: Optional[str] = Field(default=None, description="Optional comment for the approval decision")


class ApprovalResponse(BaseModel):
    request_id: str = Field(..., description="Unique identifier for the request")
    status: RequestStatus = Field(..., description="Updated status of the request")
    message: str = Field(..., description="Response message")


def verify_api_key(api_key: Optional[str] = Header(None, alias=API_KEY_NAME)):
    """Verify API key authentication"""
    if not api_key or api_key != VALID_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return api_key


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Aurea Orchestrator",
        "version": "1.0.0",
        "description": "Automated Unified Reasoning & Execution Agents"
    }


@app.post("/request", response_model=OrchestrationResponse, status_code=status.HTTP_201_CREATED)
async def create_request(
    request: OrchestrationRequest,
    api_key: str = Header(..., alias=API_KEY_NAME)
) -> OrchestrationResponse:
    """
    Submit a new orchestration request
    
    This endpoint allows you to submit a task for orchestration. The request will be
    queued and await approval before processing.
    """
    verify_api_key(api_key)
    
    request_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    request_data = {
        "request_id": request_id,
        "task_description": request.task_description,
        "parameters": request.parameters,
        "priority": request.priority,
        "status": RequestStatus.PENDING,
        "created_at": now,
        "updated_at": now,
        "result": None
    }
    
    requests_db[request_id] = request_data
    
    return OrchestrationResponse(
        request_id=request_id,
        status=RequestStatus.PENDING,
        message="Request created successfully and awaiting approval",
        created_at=now
    )


@app.get("/status/{request_id}", response_model=StatusResponse)
async def get_status(
    request_id: str,
    api_key: str = Header(..., alias=API_KEY_NAME)
) -> StatusResponse:
    """
    Get the status of an orchestration request
    
    This endpoint returns the current status and details of a previously submitted request.
    """
    verify_api_key(api_key)
    
    if request_id not in requests_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Request {request_id} not found"
        )
    
    request_data = requests_db[request_id]
    
    return StatusResponse(
        request_id=request_data["request_id"],
        status=request_data["status"],
        task_description=request_data["task_description"],
        created_at=request_data["created_at"],
        updated_at=request_data["updated_at"],
        result=request_data["result"]
    )


@app.post("/approve", response_model=ApprovalResponse)
async def approve_request(
    approval: ApprovalRequest,
    api_key: str = Header(..., alias=API_KEY_NAME)
) -> ApprovalResponse:
    """
    Approve or reject an orchestration request
    
    This endpoint allows you to approve or reject a pending orchestration request.
    Approved requests will move to processing status.
    """
    verify_api_key(api_key)
    
    if approval.request_id not in requests_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Request {approval.request_id} not found"
        )
    
    request_data = requests_db[approval.request_id]
    
    if request_data["status"] != RequestStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Request {approval.request_id} is not in pending status"
        )
    
    new_status = RequestStatus.APPROVED if approval.approved else RequestStatus.REJECTED
    request_data["status"] = new_status
    request_data["updated_at"] = datetime.utcnow()
    
    if approval.approved:
        # Simulate processing
        request_data["result"] = {
            "status": "processing_started",
            "comment": approval.comment
        }
        message = f"Request {approval.request_id} approved and processing started"
    else:
        request_data["result"] = {
            "status": "rejected",
            "comment": approval.comment
        }
        message = f"Request {approval.request_id} rejected"
    
    return ApprovalResponse(
        request_id=approval.request_id,
        status=new_status,
        message=message
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
