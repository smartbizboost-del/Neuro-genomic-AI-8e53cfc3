from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime
import uuid
import json
from typing import Optional, Dict, Any
import random
import math

app = FastAPI(title="Neuro-Genomic AI API", version="2.0.0")

# CORS for dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for demo
analysis_results = {}

# Health check
@app.get("/")
@app.get("/health")
@app.get("/api/v1/health")
async def health():
    return {
        "status": "healthy",
        "service": "neuro-genomic-ai",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    }

# System status
@app.get("/api/v1/status")
async def system_status():
    return {
        "api_ok": True,
        "model_loaded": True,
        "inference_status": "ready",
        "active_sessions": 1,
        "uptime": "2h 30m",
        "system": {
            "status": "operational",
            "cpu_usage": 25,
            "memory_usage": 45
        }
    }

# Upload ECG file
@app.post("/api/v1/upload")
async def upload_ecg(file: UploadFile = File(...)):
    try:
        file_id = str(uuid.uuid4())
        content = await file.read()
        
        # Store basic info
        analysis_results[file_id] = {
            "filename": file.filename,
            "status": "uploaded",
            "upload_time": datetime.now().isoformat(),
            "file_size": len(content)
        }
        
        return JSONResponse({
            "success": True,
            "file_id": file_id,
            "filename": file.filename,
            "message": "File uploaded successfully",
            "status": "ready_for_analysis"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Analyze ECG
@app.post("/api/v1/analyze/{file_id}")
async def analyze_ecg(file_id: str):
    if file_id not in analysis_results:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Simulate analysis
    analysis_results[file_id].update({
        "status": "completed",
        "analysis_time": datetime.now().isoformat(),
        "results": {
            "classification": random.choice(["Normal", "Arrhythmia", "Tachycardia", "Bradycardia"]),
            "confidence": round(random.uniform(0.85, 0.99), 3),
            "heart_rate": random.randint(60, 100),
            "signal_quality": round(random.uniform(0.90, 0.99), 3),
            "recommendations": [
                "Regular monitoring recommended",
                "Consult healthcare provider for detailed analysis"
            ]
        }
    })

    # Derive richer, frontend-friendly fields for visualization
    try:
        res = analysis_results[file_id].get("results", {})
        cls = str(res.get("classification", "unknown")).lower()
        conf = float(res.get("confidence", 0.9))
        base_map = {
            "normal": 0.78,
            "arrhythmia": 0.45,
            "tachycardia": 0.5,
            "bradycardia": 0.5,
        }
        dev = round(base_map.get(cls, 0.5) * conf, 3)
        analysis_results[file_id]["developmental_index"] = dev
        analysis_results[file_id]["confidence"] = conf

        # simple HRV feature placeholders
        analysis_results[file_id]["hrv_metrics"] = {
            "rmssd": round(20 + conf * 40, 1),
            "sdnn": round(70 + conf * 50, 1),
            "lf_hf_ratio": round(1.0 + (0.5 * (1 - conf)), 2),
        }
        analysis_results[file_id]["features"] = analysis_results[file_id]["hrv_metrics"]

        # cleaned_ecg: synthetic waveform for demo visualisation
        ecg = []
        phase = random.random() * 2 * math.pi
        for i in range(500):
            ecg.append(round(math.sin(i * 0.02 + phase) * 0.8 + random.uniform(-0.05, 0.05), 4))
        analysis_results[file_id]["cleaned_ecg"] = ecg

        # interpretation and recommendation
        recs = res.get("recommendations", [])
        analysis_results[file_id]["interpretation"] = recs or [f"Classification: {res.get('classification')}"]
        analysis_results[file_id]["recommendation"] = recs[0] if recs else None
    except Exception:
        pass

    return JSONResponse(analysis_results[file_id])

# Get analysis results
@app.get("/api/v1/analysis/{file_id}")
async def get_analysis(file_id: str):
    if file_id not in analysis_results:
        raise HTTPException(status_code=404, detail="File not found")
    
    return JSONResponse(analysis_results[file_id])

# Get all analyses
@app.get("/api/v1/analyses")
async def list_analyses():
    return JSONResponse({
        "total": len(analysis_results),
        "analyses": [
            {
                "file_id": fid,
                "filename": data.get("filename"),
                "status": data.get("status"),
                "timestamp": data.get("upload_time")
            }
            for fid, data in analysis_results.items()
        ]
    })

# Generate report
@app.post("/api/v1/report/{file_id}")
async def generate_report(file_id: str):
    if file_id not in analysis_results:
        raise HTTPException(status_code=404, detail="File not found")
    
    data = analysis_results[file_id]
    report = {
        "report_id": str(uuid.uuid4()),
        "file_id": file_id,
        "generated_at": datetime.now().isoformat(),
        "content": {
            "summary": f"Analysis of {data.get('filename')} completed successfully",
            "findings": data.get("results", {}),
            "clinical_significance": "Further evaluation recommended based on findings"
        }
    }
    
    return JSONResponse(report)

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Neuro-Genomic AI API Server")
    print("=" * 50)
    print(f"📍 Server: http://0.0.0.0:8000")
    print(f"📊 API Docs: http://0.0.0.0:8000/docs")
    print(f"❤️  Health: http://0.0.0.0:8000/health")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
