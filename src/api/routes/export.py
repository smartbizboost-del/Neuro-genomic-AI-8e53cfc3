from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from pathlib import Path

router = APIRouter()

@router.get("/export/pdf")
async def export_pdf(file_id: str):
    """Export analysis as PDF"""
    # Placeholder - replace with actual PDF generation using reportlab
    file_path = f"/tmp/report_{file_id}.pdf"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(file_path, media_type="application/pdf", filename=f"report_{file_id}.pdf")

@router.get("/export/csv")
async def export_csv(file_id: str):
    """Export analysis as CSV"""
    # Placeholder
    file_path = f"/tmp/data_{file_id}.csv"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Data not found")
    return FileResponse(file_path, media_type="text/csv", filename=f"data_{file_id}.csv")
