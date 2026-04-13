"""
FHIR export functionality for surveillance integration
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List
import redis
import logging

from src.fhir.resources import (
    create_patient_resource,
    create_observation_resource,
    create_risk_assessment_resource,
    create_diagnostic_report,
)

logger = logging.getLogger(__name__)


def _normalize_feature_name(key: str) -> str:
    return key.replace('-', '_').replace(' ', '_').upper()


class FHIRExporter:
    """Export analysis results as FHIR bundles"""

    def __init__(self, output_dir: str = "data/fhir_exports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def create_bundle(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a FHIR Bundle containing all resources
        """
        patient_id = analysis_result.get('patient_id', analysis_result.get('file_id', 'unknown'))
        gestational_weeks = analysis_result.get('gestational_weeks', 34)

        patient = create_patient_resource(
            patient_id=patient_id,
            gestational_weeks=gestational_weeks,
            maternal_age=analysis_result.get('maternal_age'),
            maternal_bmi=analysis_result.get('maternal_bmi')
        )

        observations: List[Dict[str, Any]] = []
        features = analysis_result.get('features', {}) or {}

        normal_ranges = {
            'RMSSD': (2.4, 4.8),
            'SDNN': (30, 50),
            'LF_HF': (0.8, 1.5),
            'SAMPLE_ENTROPY': (1.0, 1.5),
            'AC_T9': (20, 40),
            'DC_T9': (20, 40)
        }

        for feature_name, value in features.items():
            feature_key = _normalize_feature_name(feature_name)
            if feature_key in normal_ranges and isinstance(value, (int, float)):
                low, high = normal_ranges[feature_key]
                unit = "ms" if feature_key in ['RMSSD', 'SDNN', 'AC_T9', 'DC_T9'] else "ratio"
                observations.append(create_observation_resource(
                    patient_id=patient_id,
                    feature_name=feature_key,
                    value=value,
                    unit=unit,
                    reference_range_low=low,
                    reference_range_high=high,
                    gestational_weeks=gestational_weeks
                ))

        risk_assessments: List[Dict[str, Any]] = []
        risk_data = analysis_result.get('risk', {}) or {}

        if isinstance(risk_data, dict):
            if 'IUGR' in risk_data or 'iugr' in risk_data:
                score = float(risk_data.get('IUGR', risk_data.get('iugr', 0)))
                risk_assessments.append(create_risk_assessment_resource(
                    patient_id=patient_id,
                    risk_type='IUGR',
                    risk_score=score,
                    confidence_interval=95,
                    interpretation=analysis_result.get('risk_classification', 'Unknown')
                ))
            if 'preterm' in risk_data:
                score = float(risk_data.get('preterm', 0))
                risk_assessments.append(create_risk_assessment_resource(
                    patient_id=patient_id,
                    risk_type='preterm',
                    risk_score=score,
                    confidence_interval=95,
                    interpretation=analysis_result.get('risk_classification', 'Unknown')
                ))
            if 'hypoxia' in risk_data:
                score = float(risk_data.get('hypoxia', 0))
                risk_assessments.append(create_risk_assessment_resource(
                    patient_id=patient_id,
                    risk_type='hypoxia',
                    risk_score=score,
                    confidence_interval=95,
                    interpretation=analysis_result.get('risk_classification', 'Unknown')
                ))

            if 'predicted_class' in risk_data:
                score = max(0.0, min(100.0, float(risk_data.get('pathological', 0) * 100)))
                risk_assessments.append(create_risk_assessment_resource(
                    patient_id=patient_id,
                    risk_type='overall',
                    risk_score=score,
                    confidence_interval=95,
                    interpretation=risk_data.get('predicted_class', 'Unknown')
                ))

        report = create_diagnostic_report(
            patient_id=patient_id,
            observations=observations,
            risk_assessments=risk_assessments,
            developmental_index=float(analysis_result.get('developmental_index', 0.0)),
            recommendations=analysis_result.get('recommendations', 'Continue routine monitoring')
        )

        bundle = {
            "resourceType": "Bundle",
            "id": f"bundle-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "type": "batch",
            "timestamp": datetime.now().isoformat(),
            "entry": [
                {"resource": patient, "request": {"method": "POST", "url": "Patient"}},
                *[{"resource": obs, "request": {"method": "POST", "url": "Observation"}} for obs in observations],
                *[{"resource": risk, "request": {"method": "POST", "url": "RiskAssessment"}} for risk in risk_assessments],
                {"resource": report, "request": {"method": "POST", "url": "DiagnosticReport"}}
            ]
        }

        return bundle

    def export_to_file(self, analysis_result: Dict[str, Any]) -> str:
        """
        Export analysis result to FHIR JSON file
        """
        bundle = self.create_bundle(analysis_result)
        filename = f"{self.output_dir}/{analysis_result.get('file_id', 'unknown')}.fhir.json"

        with open(filename, 'w') as f:
            json.dump(bundle, f, indent=2)

        return filename

    def export_to_kenya_emr(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format specifically for KenyaEMR / DHIS2 integration
        """
        bundle = self.create_bundle(analysis_result)

        for entry in bundle['entry']:
            resource = entry['resource']
            if resource.get('resourceType') == 'Observation':
                resource['extension'] = resource.get('extension', [])
                resource['extension'].append({
                    "url": "http://kenyaemr.org/fhir/StructureDefinition/facility-code",
                    "valueCodeableConcept": {
                        "coding": [{
                            "system": "http://kenyaemr.org/facility-codes",
                            "code": "KNH-001"
                        }]
                    }
                })

        return bundle
