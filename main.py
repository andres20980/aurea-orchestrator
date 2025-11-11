"""
Aurea Orchestrator - Main Application
FastAPI application with data compliance layer
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import init_db
from app.api import compliance, data


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup/shutdown"""
    # Startup
    init_db()
    yield
    # Shutdown (if needed)


app = FastAPI(
    title="Aurea Orchestrator",
    description="""
    Automated Unified Reasoning & Execution Agents with Data Compliance Layer
    
    ## Features
    
    * **Data Anonymization**: Automatically anonymize sensitive PII
    * **Consent Management**: Track and manage user consents (GDPR compliance)
    * **Audit Logging**: Complete audit trail of model inputs/outputs
    * **Data Purging**: Automated retention and purging of old data
    * **Compliance Reporting**: Real-time compliance status reports
    
    ## Compliance
    
    This API implements GDPR and SOC2 compliance requirements including:
    - Right to erasure (Article 17)
    - Data minimization (Article 5)
    - Consent management (Article 7)
    - Record-keeping (Article 30)
    """,
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(compliance.router)
app.include_router(data.router)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Aurea Orchestrator",
        "version": "1.0.0",
        "status": "operational",
        "compliance": {
            "gdpr_compliant": True,
            "soc2_ready": True,
            "features": [
                "data_anonymization",
                "consent_logging",
                "audit_trail",
                "automated_purging"
            ]
        },
        "endpoints": {
            "compliance_report": "/compliance/report",
            "data_purge": "/data/purge",
            "consent_management": "/compliance/consent",
            "audit_logs": "/compliance/audit"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
