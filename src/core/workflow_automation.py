from datetime import datetime
from src.workers.celery_app import celery_app


def generate_clinical_note(analysis_results: dict) -> str:
    """Auto-generate clinical note for patient file."""
    note_template = (
        "NEURO-GENOMIC AI CLINICAL NOTE\n"
        "Date: {date}\n"
        "Gestational Age: {ga} weeks\n\n"
        "Developmental Assessment:\n"
        "- Developmental Index: {dev_index:.2f}\n"
        "- Risk Classification: {risk_class}\n"
        "- Confidence: {confidence:.2f}\n\n"
        "Key Findings:\n"
        "{findings}\n\n"
        "Recommendations:\n"
        "{recommendations}\n"
    )

    findings = '\n'.join([f"- {item}" for item in analysis_results.get('interpretation', [])])
    recommendations = analysis_results.get('recommendations', 'Follow up in accordance with clinical protocol.')

    return note_template.format(
        date=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
        ga=analysis_results.get('gestational_weeks', 0),
        dev_index=analysis_results.get('developmental_index', 0.0),
        risk_class=analysis_results.get('risk', {}).get('predicted_class', 'unknown'),
        confidence=analysis_results.get('risk', {}).get('normal', 0.0) * 100.0,
        findings=findings,
        recommendations=recommendations
    )


@celery_app.task(name='send_alert_if_pathological')
def send_alert_if_pathological(analysis_id: str, patient_id: str, clinician_email: str) -> dict:
    """Auto-send alert for pathological findings."""
    # In a production system, this would send email/SMS and create notification records.
    return {
        'analysis_id': analysis_id,
        'patient_id': patient_id,
        'clinician_email': clinician_email,
        'status': 'alert_queued',
        'timestamp': datetime.utcnow().isoformat()
    }


def suggest_follow_up_schedule(risk_class: str, gestational_weeks: int) -> int:
    """Smart scheduling based on risk level."""
    schedule_map = {
        'normal': 4,
        'suspect': 2,
        'pathological': 1
    }
    return schedule_map.get(risk_class, 4)
