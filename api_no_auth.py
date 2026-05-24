from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn
from datetime import datetime
import json

app = FastAPI(title="Neuro-Genomic AI API - Dev Mode (No Auth)")

# Allow all CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock user for all requests
@app.middleware("http")
async def mock_auth(request: Request, call_next):
    """Bypass all authentication in development"""
    # Add mock user to request state
    request.state.user = {
        "id": "dev_user",
        "role": "admin",
        "email": "dev@example.com"
    }
    response = await call_next(request)
    return response

# Health endpoints
@app.get("/")
@app.get("/health")
@app.get("/api/v1/health")
@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "service": "neuro-genomic-ai",
        "auth": "disabled",
        "timestamp": datetime.now().isoformat()
    }

# Status endpoint
@app.get("/api/v1/status")
async def status():
    return {
        "api_ok": True,
        "model_loaded": True,
        "inference_status": "ready",
        "auth_required": False,
        "system": {
            "status": "operational",
            "version": "1.0.0-dev"
        }
    }

# Upload endpoint
@app.post("/api/v1/upload")
async def upload_file(file: UploadFile = File(...)):
    return {
        "file_id": f"dev_{datetime.now().timestamp()}",
        "filename": file.filename,
        "status": "uploaded",
        "message": "File uploaded successfully (auth bypassed)"
    }

# Analysis endpoint
@app.get("/api/v1/analysis/{file_id}")
async def get_analysis(file_id: str):
    return {
        "file_id": file_id,
        "status": "completed",
        "results": {
            "classification": "normal",
            "confidence": 0.95,
            "timestamp": datetime.now().isoformat()
        }
    }

# Mock predictions endpoint
@app.post("/api/v1/predict")
async def predict():
    return {
        "prediction": "normal",
        "confidence": 0.92,
        "features": {
            "heart_rate": 72,
            "qt_interval": 408,
            "signal_quality": 0.98
        }
    }

if __name__ == "__main__":
    print("🚀 Starting API with AUTH DISABLED for development")
    print("📍 Listening on http://0.0.0.0:8000")
    print("🔓 Authentication is BYPASSED - DO NOT USE IN PRODUCTION")
    uvicorn.run(app, host="0.0.0.0", port=8000)
