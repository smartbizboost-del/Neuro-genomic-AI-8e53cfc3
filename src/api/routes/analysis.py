"""
Analysis endpoints
"""

from fastapi import APIRouter, HTTPException
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
    
    # If not found in Redis, it means it's either still queueing or failed
    raise HTTPException(status_code=404, detail="Analysis results not found. It may still be processing or failed.")