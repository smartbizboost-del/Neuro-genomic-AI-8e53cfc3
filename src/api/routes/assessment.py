from datetime import datetime

from fastapi import APIRouter, Depends

from src.core.risk_engine import classify_risk, developmental_index
from src.api.middleware.auth import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/assessment")
async def get_assessment():
    preeclampsia_score = 82
    growth_index = 78
    oxygen_index = 72
    movement_index = 69
    maternal_stability = 83
    developmental_score = developmental_index(
        growth=growth_index,
        oxygen=oxygen_index,
        movement=movement_index,
        maternal_stability=maternal_stability,
    )

    return {
        "patient_id": "NGA-001",
        "maternal_risk": "HIGH",
        "fetal_risk": "MODERATE",
        "preeclampsia_score": preeclampsia_score,
        "hypoxia_risk": 61,
        "iugr_risk": 44,
        "preterm_risk": 58,
        "ctg_status": "Suspicious",
        "developmental_index": int(developmental_score),
        "decision": classify_risk(preeclampsia_score),
        "timestamp": datetime.utcnow().isoformat(),
        "maternal_vitals": {
            "blood_pressure": "138/88",
            "oxygen_saturation": 94,
            "heart_rate": 92,
            "temperature": 36.8,
        },
        "fetal_metrics": {
            "fetal_heart_rate": 142,
            "variability": 16,
            "acceleration_count": 3,
            "movement_score": 78,
        },
    }
