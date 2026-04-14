"""
Neuro-Genomic AI API
FastAPI Application Entry Point
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging
import time
from contextlib import asynccontextmanager

from src.api.routes import health, upload, analysis, export, auth, contact
from src.api.middleware.auth import auth_middleware
from src.api.middleware.logging import log_requests
from src.core.pipeline import get_pipeline
from src.utils.logger import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Get singleton pipeline instance
pipeline = get_pipeline()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Starting Neuro-Genomic AI API")
    logger.info("Pipeline ready. Models will be lazy-loaded on first analysis request.")
    yield
    # Shutdown
    logger.info("Shutting down Neuro-Genomic AI API")

# Create FastAPI app
app = FastAPI(
    title="Neuro-Genomic AI API",
    description="AI-powered fetal development monitoring system",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately in production
)

# Custom middleware
@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(upload.router, prefix="/api/v1", tags=["upload"])
app.include_router(analysis.router, prefix="/api/v1", tags=["analysis"])
app.include_router(export.router, prefix="/api/v1", tags=["export"])
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(contact.router, prefix="/api/v1", tags=["contact"])

@app.get("/")
async def root():
    return {
        "name": "Neuro-Genomic AI",
        "version": "2.0.0",
        "status": "operational",
        "docs": "/docs"
    }

@app.get("/ready")
async def readiness():
    """Kubernetes readiness probe"""
    return {"status": "ready"}

@app.get("/health")
async def liveness():
    """Kubernetes liveness probe"""
    return {"status": "healthy"}