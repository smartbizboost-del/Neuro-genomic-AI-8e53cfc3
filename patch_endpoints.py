# Add this to your src/api/main.py or create a new route file
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["dashboard"])

@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "neuro-genomic-ai"}

@router.get("/status")
async def system_status():
    return {
        "api_ok": True,
        "model_loaded": False,
        "inference_status": "idle",
        "last_checked": "2024-01-01T00:00:00Z"
    }

# In your main.py, include this router:
# app.include_router(router)
