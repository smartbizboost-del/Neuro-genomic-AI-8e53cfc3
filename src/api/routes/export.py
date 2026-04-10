"""
Export endpoints
"""

from csv import writer as csv_writer
from io import StringIO
from typing import List

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response

from src.api.models.schemas import AnalysisResponse
from src.api.routes.analysis import get_analysis

router = APIRouter()


def _escape_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _build_pdf(lines: List[str]) -> bytes:
    text_lines = []
    y = 760
    for line in lines:
        text_lines.append(f"BT /F1 12 Tf 72 {y} Td ({_escape_pdf_text(line)}) Tj ET")
        y -= 16

    content_stream = "\n".join(text_lines)
    objects = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        f"<< /Length {len(content_stream.encode('utf-8'))} >>\nstream\n{content_stream}\nendstream",
    ]

    buffer = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(buffer))
        buffer.extend(f"{index} 0 obj\n{obj}\nendobj\n".encode("utf-8"))

    xref_offset = len(buffer)
    buffer.extend(f"xref\n0 {len(objects) + 1}\n".encode("utf-8"))
    buffer.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        buffer.extend(f"{offset:010d} 00000 n \n".encode("utf-8"))
    buffer.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF".encode("utf-8")
    )
    return bytes(buffer)


def _analysis_to_rows(analysis: AnalysisResponse) -> list[list[str]]:
    payload = jsonable_encoder(analysis)
    rows: list[list[str]] = [["section", "field", "value"]]
    for key, value in payload.get("features", {}).items():
        rows.append(["features", key, str(value)])
    for key, value in payload.get("risk", {}).items():
        rows.append(["risk", key, str(value)])
    rows.append(["summary", "file_id", payload.get("file_id", "")])
    rows.append(["summary", "developmental_index", str(payload.get("developmental_index", ""))])
    rows.append(["summary", "gestational_weeks", str(payload.get("gestational_weeks", ""))])
    rows.append(["summary", "created_at", str(payload.get("created_at", ""))])
    return rows


@router.get("/export/{file_id}/pdf")
async def export_pdf(file_id: str):
    """Export analysis results as a lightweight PDF report."""
    analysis = await get_analysis(file_id)
    payload = jsonable_encoder(analysis)
    lines = [
        "Neuro-Genomic AI Analysis Report",
        f"File ID: {payload.get('file_id', '')}",
        f"Developmental Index: {payload.get('developmental_index', '')}",
        f"Gestational Weeks: {payload.get('gestational_weeks', '')}",
        f"Predicted Class: {payload.get('risk', {}).get('predicted_class', '')}",
        f"Confidence: {payload.get('risk', {}).get('confidence_label', '')} ({payload.get('risk', {}).get('confidence_level', '')})",
        f"Unsupervised Cluster: {payload.get('risk', {}).get('unsupervised_cluster', '')}",
    ]
    pdf_bytes = _build_pdf(lines)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="analysis_{file_id}.pdf"'},
    )


@router.get("/export/{file_id}/csv")
async def export_csv(file_id: str):
    """Export HRV features and risk summary as CSV."""
    analysis = await get_analysis(file_id)
    rows = _analysis_to_rows(analysis)
    buffer = StringIO()
    csv = csv_writer(buffer)
    csv.writerows(rows)
    return Response(
        content=buffer.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="analysis_{file_id}.csv"'},
    )