import io
import json
from datetime import datetime
from typing import Any, Dict, List

try:
    from reportlab.lib import colors
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
except ImportError:
    colors = None  # type: ignore
    canvas = None  # type: ignore


def generate_pdf_report(analysis_data: Dict[str, Any]) -> bytes:
    """Generate a PDF report from analysis data."""
    buffer = io.BytesIO()
    if canvas is None:
        raise ImportError("reportlab is required to generate PDF reports")

    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle("Neuro-Genomic AI Clinical Report")
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(72, 720, "Neuro-Genomic AI Clinical Report")
    pdf.setFont("Helvetica", 10)

    y = 690
    pdf.drawString(72, y, f"Date: {datetime.utcnow().isoformat()} UTC")
    y -= 20
    pdf.drawString(72, y, f"File ID: {analysis_data.get('file_id', 'N/A')}")
    y -= 20
    pdf.drawString(72, y, f"Gestational Weeks: {analysis_data.get('gestational_weeks', 'N/A')}")
    y -= 20
    pdf.drawString(72, y, f"Developmental Index: {analysis_data.get('developmental_index', 0):.2f}")
    y -= 20
    pdf.drawString(72, y, f"Risk Classification: {analysis_data.get('risk', {}).get('predicted_class', 'unknown')}")
    y -= 30

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(72, y, "Key Metrics")
    y -= 20
    pdf.setFont("Helvetica", 10)
    for label, value in analysis_data.get('features', {}).items():
        pdf.drawString(72, y, f"{label}: {value}")
        y -= 14
        if y < 72:
            pdf.showPage()
            y = 720

    y -= 10
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(72, y, "Interpretation")
    y -= 20
    pdf.setFont("Helvetica", 10)
    for interp in analysis_data.get('interpretation', []):
        pdf.drawString(72, y, f"- {interp}")
        y -= 14
        if y < 72:
            pdf.showPage()
            y = 720

    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()


def generate_json_report(analysis_data: Dict[str, Any]) -> str:
    """Generate JSON formatted clinical report."""
    return json.dumps(analysis_data, indent=2, default=str)


def generate_hl7_message(analysis_data: Dict[str, Any]) -> str:
    """Generate a simplified HL7-like message from analysis data."""
    patient_id = analysis_data.get('patient_id', 'UNKNOWN')
    status = analysis_data.get('risk', {}).get('predicted_class', 'unknown')
    return (
        f"MSH|^~\\&|NeuroGenomicAI|FetalCare|EMR|Hospital|{datetime.utcnow().isoformat()}||ORU^R01|" 
        f"{analysis_data.get('file_id', 'UNKNOWN')}|P|2.5\r"
        f"PID|||{patient_id}||FETAL^^^|" 
        f"{analysis_data.get('gestational_weeks', 'N/A')} weeks\r"
        f"OBR|1|||Fetal ECG Analysis\r"
        f"OBX|1|ST|TQRS|1|{analysis_data.get('features', {}).get('t_qrs_ratio', 'N/A')}|" 
        f"|N||F\r"
        f"OBX|2|TX|RISK|1|{status}||N||F\r"
    )


def generate_clinical_report(analysis_data: Dict[str, Any], output_format: str = 'pdf') -> Any:
    """Generate clinical-ready report."""
    if output_format == 'pdf':
        return generate_pdf_report(analysis_data)
    if output_format == 'hl7':
        return generate_hl7_message(analysis_data)
    return generate_json_report(analysis_data)


def generate_batch_summary(analyses_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate batch summary for hospital departments."""
    summary = {
        'total_analyses': len(analyses_list),
        'risk_distribution': {
            'normal': 0,
            'suspect': 0,
            'pathological': 0
        },
        'average_dev_index': 0.0,
        'gestational_age_range': {'min': float('inf'), 'max': 0}
    }
    for analysis in analyses_list:
        classification = analysis.get('risk', {}).get('predicted_class', 'normal')
        if classification not in summary['risk_distribution']:
            classification = 'normal'
        summary['risk_distribution'][classification] += 1
        summary['average_dev_index'] += float(analysis.get('developmental_index', 0) or 0)
        weeks = analysis.get('gestational_weeks', 0) or 0
        summary['gestational_age_range']['min'] = min(summary['gestational_age_range']['min'], weeks)
        summary['gestational_age_range']['max'] = max(summary['gestational_age_range']['max'], weeks)

    if analyses_list:
        summary['average_dev_index'] /= len(analyses_list)
    if summary['gestational_age_range']['min'] == float('inf'):
        summary['gestational_age_range']['min'] = 0
    return summary
