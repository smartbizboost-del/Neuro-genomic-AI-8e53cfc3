"""
Analysis endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import Optional
import uuid

from src.api.models.schemas import AnalysisResponse

router = APIRouter()

@router.get("/analysis/{file_id}", response_model=AnalysisResponse)
async def get_analysis(file_id: str):
    """
    Get analysis results for a processed file
    """
    # This would query the database for actual results
    # Placeholder implementation
    
    # Validate UUID format
    try:
        uuid.UUID(file_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid file ID format")
    
    # Mock response - replace with actual database query
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
            "predicted_class": "normal"
        },
        interpretation=[
            "RMSSD indicates good vagal tone",
            "LF/HF ratio suggests healthy autonomic balance",
            "Developmental index is within normal range"
        ],
        developmental_index=0.72,
        gestational_weeks=32,
        created_at="2024-01-01T00:00:00Z",
        confidence_intervals=None
    )