"""
FHIR Resource definitions for Neuro-Genomic AI
Compatible with FHIR R4 (Release 4)
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid


def generate_fhir_id() -> str:
    """Generate a FHIR-compatible ID"""
    return str(uuid.uuid4())


def create_patient_resource(patient_id: str, gestational_weeks: int,
                           maternal_age: Optional[int] = None,
                           maternal_bmi: Optional[float] = None) -> Dict[str, Any]:
    """
    Create FHIR Patient resource
    """
    resource = {
        "resourceType": "Patient",
        "id": generate_fhir_id(),
        "identifier": [{
            "system": "http://hospital.org/patient-ids",
            "value": patient_id
        }],
        "extension": [
            {
                "url": "http://hl7.org/fhir/StructureDefinition/patient-gestationalAge",
                "valueInteger": gestational_weeks
            }
        ]
    }

    if maternal_age is not None:
        resource["extension"].append({
            "url": "http://hl7.org/fhir/StructureDefinition/patient-birthTime",
            "valueDateTime": f"{datetime.now().year - maternal_age}-01-01"
        })

    if maternal_bmi is not None:
        resource["extension"].append({
            "url": "http://hl7.org/fhir/StructureDefinition/observation-bmi",
            "valueDecimal": maternal_bmi
        })

    return resource


def create_observation_resource(patient_id: str,
                                feature_name: str,
                                value: float,
                                unit: str,
                                reference_range_low: float,
                                reference_range_high: float,
                                gestational_weeks: int) -> Dict[str, Any]:
    """
    Create FHIR Observation resource for HRV features
    """
    feature_key = feature_name.upper().replace(" ", "_")
    loinc_codes = {
        'RMSSD': {'code': '80456-6', 'display': 'Heart rate variability - RMSSD'},
        'SDNN': {'code': '80455-8', 'display': 'Heart rate variability - SDNN'},
        'LF_HF': {'code': '80458-2', 'display': 'LF/HF ratio'},
        'SAMPLE_ENTROPY': {'code': '80457-4', 'display': 'Sample entropy'},
        'AC_T9': {'code': '80459-0', 'display': 'Acceleration capacity (PRSA)'},
        'DC_T9': {'code': '80460-8', 'display': 'Deceleration capacity (PRSA)'}
    }

    loinc = loinc_codes.get(feature_key, {'code': '83000-0', 'display': 'Fetal HRV parameter'})

    return {
        "resourceType": "Observation",
        "id": generate_fhir_id(),
        "status": "final",
        "category": [{
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                "code": "vital-signs",
                "display": "Vital Signs"
            }]
        }],
        "code": {
            "coding": [{
                "system": "http://loinc.org",
                "code": loinc['code'],
                "display": loinc['display']
            }]
        },
        "subject": {
            "reference": f"Patient/{patient_id}"
        },
        "effectiveDateTime": datetime.now().isoformat(),
        "valueQuantity": {
            "value": value,
            "unit": unit,
            "system": "http://unitsofmeasure.org",
            "code": unit
        },
        "referenceRange": [{
            "low": {"value": reference_range_low, "unit": unit},
            "high": {"value": reference_range_high, "unit": unit},
            "text": f"Normal range for {gestational_weeks} weeks"
        }],
        "note": [{
            "text": f"Gestational age: {gestational_weeks} weeks"
        }]
    }


def create_risk_assessment_resource(patient_id: str,
                                    risk_type: str,
                                    risk_score: float,
                                    confidence_interval: float,
                                    interpretation: str) -> Dict[str, Any]:
    """
    Create FHIR RiskAssessment resource
    """
    risk_codes = {
        'IUGR': 'FGR',
        'preterm': 'PTB',
        'hypoxia': 'HYPOX',
        'overall': 'OVR'
    }

    return {
        "resourceType": "RiskAssessment",
        "id": generate_fhir_id(),
        "status": "final",
        "subject": {
            "reference": f"Patient/{patient_id}"
        },
        "code": {
            "coding": [{
                "system": "http://neuro-genomic.ai/risk-codes",
                "code": risk_codes.get(risk_type, risk_type.upper()),
                "display": f"{risk_type.upper()} risk"
            }]
        },
        "prediction": [{
            "outcome": {
                "text": f"Risk of {risk_type}"
            },
            "probabilityDecimal": risk_score / 100,
            "qualitativeRisk": {
                "coding": [{
                    "code": interpretation.upper()
                }]
            },
            "extension": [{
                "url": "http://neuro-genomic.ai/confidence-interval",
                "valueDecimal": confidence_interval / 100
            }]
        }]
    }


def create_diagnostic_report(patient_id: str,
                             observations: List[Dict[str, Any]],
                             risk_assessments: List[Dict[str, Any]],
                             developmental_index: float,
                             recommendations: str) -> Dict[str, Any]:
    """
    Create FHIR DiagnosticReport containing all results
    """
    return {
        "resourceType": "DiagnosticReport",
        "id": generate_fhir_id(),
        "status": "final",
        "category": [{
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/v2-0074",
                "code": "FH",
                "display": "Fetal Health"
            }]
        }],
        "code": {
            "coding": [{
                "system": "http://loinc.org",
                "code": "83000-0",
                "display": "Fetal developmental assessment panel"
            }]
        },
        "subject": {
            "reference": f"Patient/{patient_id}"
        },
        "effectiveDateTime": datetime.now().isoformat(),
        "result": observations + risk_assessments,
        "conclusion": f"Developmental Index: {developmental_index}. {recommendations}",
        "presentedForm": [{
            "title": "Neuro-Genomic AI Analysis Report",
            "creation": datetime.now().isoformat()
        }]
    }
