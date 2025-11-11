"""FastAPI application for aurea-orchestrator Knowledge Base."""
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from kb import KnowledgeBase


app = FastAPI(
    title="Aurea Orchestrator Knowledge Base",
    description="Knowledge Base API for storing and querying embedded project files",
    version="1.0.0"
)

kb = KnowledgeBase()


class IndexFileRequest(BaseModel):
    """Request model for indexing a single file."""
    file_path: str
    content: str


class IndexDirectoryRequest(BaseModel):
    """Request model for indexing a directory."""
    directory_path: str
    extensions: Optional[List[str]] = None


class QueryRequest(BaseModel):
    """Request model for querying the knowledge base."""
    query: str
    top_k: Optional[int] = 5


class QueryResult(BaseModel):
    """Response model for query results."""
    id: int
    file_path: str
    content: str
    similarity: float


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Aurea Orchestrator Knowledge Base API",
        "endpoints": {
            "/kb/index": "POST - Index files or directories",
            "/kb/query": "POST - Query the knowledge base"
        }
    }


@app.post("/kb/index")
async def index_content(request: IndexFileRequest = None, directory_request: IndexDirectoryRequest = None):
    """
    Index files into the knowledge base.
    
    Can index a single file or an entire directory.
    """
    try:
        if request:
            # Index single file
            file_id = kb.index_file(request.file_path, request.content)
            return {
                "status": "success",
                "message": "File indexed successfully",
                "id": file_id,
                "file_path": request.file_path
            }
        elif directory_request:
            # Index directory
            result = kb.index_directory(
                directory_request.directory_path,
                directory_request.extensions
            )
            return {
                "status": "success",
                "message": "Directory indexed successfully",
                **result
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Must provide either file or directory to index"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/kb/query", response_model=List[QueryResult])
async def query_knowledge_base(request: QueryRequest):
    """
    Query the knowledge base for similar content.
    
    Returns the top-k most similar files based on embedding similarity.
    """
    try:
        results = kb.query(request.query, request.top_k)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
