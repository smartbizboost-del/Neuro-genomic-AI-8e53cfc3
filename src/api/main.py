"""
Neuro-Genomic AI API
FastAPI Application Entry Point
"""

from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import asyncio
import logging
import time
from contextlib import asynccontextmanager

from src.api.routes import health, upload, analysis, export, admin, auth, analytics, notifications
from src.api.middleware.logging import log_requests
from src.api.services.monitoring import (
    record_request,
    get_prometheus_metrics,
    get_live_metrics,
)
from src.api.routes.admin import MOCK_USERS
from src.core.pipeline import NeuroGenomicPipeline
from src.utils.logger import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Global pipeline instance
pipeline = NeuroGenomicPipeline()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Starting Neuro-Genomic AI API")
    try:
        pipeline.load_models()  # Load trained models from disk
        logger.info("Model pipeline ready")
    except Exception as e:
        logger.warning(f"Failed to load pre-trained models: {e}")
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

# Application request logging
app.middleware("http")(log_requests)

@app.middleware("http")
async def metrics_middleware(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    elapsed = time.time() - start_time
    record_request(request.method, request.url.path, response.status_code, elapsed)
    return response

@app.get("/metrics")
async def prometheus_metrics():
    """Prometheus scrape endpoint."""
    return get_prometheus_metrics()

@app.websocket("/ws/metrics")
async def metrics_stream(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return

    from src.api.middleware.auth import verify_token
    payload = verify_token(token)
    if payload is None:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    try:
        while True:
            active_users = sum(1 for u in MOCK_USERS.values() if u.get("status") == "active")
            await websocket.send_json(get_live_metrics(active_users))
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        logger.info("Metrics websocket disconnected")

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(upload.router, prefix="/api/v1", tags=["upload"])
app.include_router(analysis.router, prefix="/api/v1", tags=["analysis"])
app.include_router(export.router, prefix="/api/v1", tags=["export"])
app.include_router(admin.router, prefix="/api/v1", tags=["admin"])
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(analytics.router, prefix="/api/v1", tags=["analytics"])
app.include_router(notifications.router, prefix="/api/v1", tags=["notifications"])

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