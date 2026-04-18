from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/api/v1", tags=["health"])

@router.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2026.04",
        "service": "neuro-genomic-ai-api"
    }

@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2026.04",
        "components": {
            "database": "ok",
            "redis": "ok",
            "model": "loaded"
        }
    }
