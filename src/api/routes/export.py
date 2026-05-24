from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
import os
import csv
import tempfile
from typing import Dict, Any, Optional

from src.fhir.exporter import FHIRExporter
from src.api.middleware.auth import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])


def _get_analysis_result(analysis_id: str) -> Optional[Dict[str, Any]]:
    """Placeholder analysis retrieval helper."""
    return None


@router.get("/export/fhir")
async def export_fhir(analysis_id: str):
    analysis_result = _get_analysis_result(analysis_id)
    if not analysis_result:
        raise HTTPException(status_code=404, detail="Analysis result not found")

    exporter = FHIRExporter()
    bundle = exporter.create_bundle(analysis_result)
    return bundle


@router.get("/export/json/{analysis_id}")
async def export_json(analysis_id: str):
    analysis_result = _get_analysis_result(analysis_id)
    if not analysis_result:
        raise HTTPException(status_code=404, detail="Analysis result not found")
    return analysis_result


@router.get("/export/csv/{analysis_id}")
async def export_csv(analysis_id: str):
    analysis_result = _get_analysis_result(analysis_id)
    if not analysis_result:
        raise HTTPException(status_code=404, detail="Analysis result not found")

    filename = os.path.join(tempfile.gettempdir(), f"analysis_{analysis_id}.csv")
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["field", "value"])
        for key, value in analysis_result.items():
            if isinstance(value, (str, int, float, bool)) or value is None:
                writer.writerow([key, value])
            elif isinstance(value, dict):
                for subkey, subvalue in value.items():
                    writer.writerow([f"{key}.{subkey}", subvalue])
            elif isinstance(value, list):
                writer.writerow([key, "; ".join(map(str, value))])

    return FileResponse(filename, media_type="text/csv", filename=os.path.basename(filename))


@router.get("/export/pdf/{analysis_id}")
async def export_pdf(analysis_id: str):
    file_path = os.path.join(tempfile.gettempdir(), f"report_{analysis_id}.pdf")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(file_path, media_type="application/pdf", filename=os.path.basename(file_path))
