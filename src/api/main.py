from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from src.api.routes import health, analysis, upload, export, contact
from src.api.routes.assessment import router as assessment_router
from src.api.routes.auth import router as auth_router
from src.core.pipeline import get_pipeline, NeuroGenomicPipeline

app = FastAPI(
    title="Neuro-Genomic AI API",
    version="2.0.0",
    description="Neuro-Genomic AI API for fetal ECG analysis, upload, and export"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

pipeline = get_pipeline()

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = datetime.utcnow()
    response = await call_next(request)
    process_time = (datetime.utcnow() - start_time).total_seconds()
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Include routes
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(analysis.router, prefix="/api/v1", tags=["analysis"])
app.include_router(upload.router, prefix="/api/v1", tags=["upload"])
app.include_router(export.router, prefix="/api/v1", tags=["export"])
app.include_router(contact.router, prefix="/api/v1", tags=["contact"])
app.include_router(assessment_router, prefix="/api", tags=["assessment"])
app.include_router(auth_router)

@app.get("/")
async def root():
    return {"name": app.title, "version": app.version, "status": "operational"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/ready")
async def readiness_check():
    return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}
