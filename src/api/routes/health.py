"""
Health check endpoints
"""

from fastapi import APIRouter
import psutil
import time

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "neuro-genomic-ai"
    }

@router.get("/health/detailed")
async def detailed_health():
    """Detailed health check with system metrics"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "neuro-genomic-ai",
        "system": {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        }
    }