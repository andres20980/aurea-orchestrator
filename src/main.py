"""Main entry point for the Aurea Sandbox Orchestrator."""

import uvicorn
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from sandbox.api import app


def main():
    """Run the API server."""
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("RELOAD", "false").lower() == "true",
    )


if __name__ == "__main__":
    main()
