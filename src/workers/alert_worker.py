from src.workers.celery_app import celery_app
from src.core.workflow_automation import generate_clinical_note


@celery_app.task(name='alert_worker.send_alert_if_pathological')
def send_alert_if_pathological(analysis_id: str, patient_id: str, clinician_email: str):
    """Celery task for sending alert notifications."""
    note = generate_clinical_note({
        'analysis_id': analysis_id,
        'patient_id': patient_id,
        'gestational_weeks': None,
        'developmental_index': 0.0,
        'risk': {'predicted_class': 'unknown', 'normal': 0.0},
        'interpretation': []
    })
    # Placeholder for actual alert delivery logic
    return {
        'analysis_id': analysis_id,
        'patient_id': patient_id,
        'clinician_email': clinician_email,
        'note': note,
        'status': 'queued_for_delivery'
    }
