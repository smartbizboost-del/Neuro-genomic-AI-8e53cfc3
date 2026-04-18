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
        return RESULTS_DB[LATEST_FILE_ID]
    if not RESULTS_DB:
        raise HTTPException(status_code=404, detail="No analysis available")
    latest_id = next(reversed(RESULTS_DB))
    return RESULTS_DB[latest_id]

@router.get("/analysis/{file_id}", response_model=AnalysisResponse)
async def get_analysis(file_id: str):
    """
    Get analysis results for a processed file
    Returns preliminary results if full analysis isn't ready yet.
    """
    # Validate UUID format
    try:
        uuid.UUID(file_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid file ID format")
    
    # Return actual result if available (preliminary or complete)
    if file_id in RESULTS_DB:
        result_data = RESULTS_DB[file_id]
        return result_data
    
    # If not found, return 404 (don't return mock)
    raise HTTPException(status_code=404, detail="Analysis not found. Please check file_id.")


@router.get("/analysis/{file_id}/status")
async def get_analysis_status(file_id: str):
    """
    Get processing status of an analysis.
    Useful for polling to know when full results are ready.
    
    Returns:
    - status: "processing", "completed", "error"
    - is_preliminary: boolean indicating if results are preliminary or final
    - processed_at: timestamp when processing started
    """
    # Validate UUID format
    try:
        uuid.UUID(file_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid file ID format")
    
    if file_id not in RESULTS_DB:
        raise HTTPException(status_code=404, detail="File not found")
    
    result_data = RESULTS_DB[file_id]
    return {
        "file_id": file_id,
        "status": result_data.get("status", "processing"),
        "is_preliminary": result_data.get("is_preliminary", True),
        "processed_at": result_data.get("created_at"),
        "confidence": result_data.get("confidence", 0.0)
    }