"""
Analysis endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import Optional
import uuid

from src.api.models.schemas import AnalysisResponse

router = APIRouter()
RESULTS_DB = {}
LATEST_FILE_ID: Optional[str] = None

@router.get("/analysis/latest", response_model=AnalysisResponse)
async def get_latest_analysis():
    """
    Get the latest processed analysis result.
    """
    global LATEST_FILE_ID
    if LATEST_FILE_ID and LATEST_FILE_ID in RESULTS_DB:
        return AnalysisResponse(**RESULTS_DB[LATEST_FILE_ID])
    if not RESULTS_DB:
        raise HTTPException(status_code=404, detail="No analysis available")
    latest_id = next(reversed(RESULTS_DB))
    return AnalysisResponse(**RESULTS_DB[latest_id])

@router.get("/analysis/{file_id}", response_model=AnalysisResponse)
async def get_analysis(file_id: str):
    """
    Get analysis results for a processed file
    """
    # Validate UUID format
    try:
        uuid.UUID(file_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid file ID format")
    
    if file_id in RESULTS_DB:
        return AnalysisResponse(**RESULTS_DB[file_id])
    
    # Mock response - fallback
    return AnalysisResponse(
        file_id=file_id,
        features={
            "rmssd": 28.5,
            "sdnn": 35.2,
            "lf_hf_ratio": 1.2,
            "sample_entropy": 1.15,
            "mean_rr": 450.0,
            "pnn50": 12.5,
            "lf_power": 245.3,
            "hf_power": 203.6,
            "developmental_index": 0.72
        },
        risk={
            "normal": 0.85,
            "suspect": 0.12,
            "pathological": 0.03,
            "predicted_class": "normal",
            "confidence_level": 0.85,
            "confidence_label": "high",
            "anomaly_score": 0.0,
            "unsupervised_cluster": 0
        },
        interpretation=[
            "Data is still processing or unavailable. Showing Mock representation."
        ],
        developmental_index=0.72,
        gestational_weeks=32,
        created_at="2024-01-01T00:00:00Z",
        confidence_intervals=None
    )