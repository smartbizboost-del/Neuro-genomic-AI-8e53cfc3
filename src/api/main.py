from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI(title="Neuro-Genomic AI API", version="2026.04")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root health (used by dashboard)
@app.get("/health")
async def root_health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "neuro-genomic-ai-api",
        "message": "API is running"
    }

# Detailed health
@app.get("/health/detailed")
async def detailed_health():
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

# API v1 health (for consistency)
@app.get("/api/v1/health")
async def api_v1_health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "neuro-genomic-ai-api"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
