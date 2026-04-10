"""
Analysis endpoints
"""

from fastapi import APIRouter, HTTPException
RESULTS_DB = {}
from typing import Optional
import uuid

from src.api.models.schemas import AnalysisResponse

router = APIRouter()
import json
import redis
import os
import logging

logger = logging.getLogger(__name__)

@router.get("/analysis/{file_id}", response_model=AnalysisResponse)
async def get_analysis(file_id: str):
    """
    Get analysis results for a processed file via Redis cache
    """
    # Validate UUID format
    try:
        uuid.UUID(file_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid file ID format")
    
    try:
        r = redis.Redis.from_url(os.getenv('REDIS_URL', 'redis://redis:6379/0'))
        result_data = r.get(f"result:{file_id}")
        
        if result_data:
            data = json.loads(result_data)
            return AnalysisResponse(**data)
            
    except Exception as e:
        logger.error(f"Redis connection error when fetching {file_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server cache error")
    
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
            "t_qrs_ratio": 0.22,
            "hypoxia_risk": "low",
            "developmental_index": 0.72
        },
        risk={
            "normal": 0.85,
            "suspect": 0.12,
            "pathological": 0.03,
            "predicted_class": "normal",
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
