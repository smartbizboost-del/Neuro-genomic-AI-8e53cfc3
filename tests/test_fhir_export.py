import asyncio
from httpx import AsyncClient, ASGITransport
from src.api.main import app
from src.api.routes import export as export_route
from src.fhir.exporter import FHIRExporter


def test_fhir_bundle_contains_patient_and_report():
    exporter = FHIRExporter(output_dir="/tmp")
    analysis_result = {
        "file_id": "test123",
        "patient_id": "patient-abc",
        "gestational_weeks": 34,
        "features": {
            "rmssd": 3.0,
            "sdnn": 40.0,
            "lf_hf_ratio": 1.1,
            "sample_entropy": 1.2,
            "ac_t9": 25.0,
            "dc_t9": 22.0
        },
        "risk": {
            "predicted_class": "normal",
            "pathological": 0.05
        },
        "developmental_index": 0.75,
        "recommendations": "Continue routine monitoring"
    }

    bundle = exporter.create_bundle(analysis_result)

    assert bundle["resourceType"] == "Bundle"
    assert any(entry["resource"]["resourceType"] == "Patient" for entry in bundle["entry"])
    assert any(entry["resource"]["resourceType"] == "Observation" for entry in bundle["entry"])
    assert any(entry["resource"]["resourceType"] == "DiagnosticReport" for entry in bundle["entry"])


def test_export_fhir_endpoint_returns_bundle(monkeypatch):
    analysis_result = {
        "file_id": "test123",
        "patient_id": "patient-abc",
        "gestational_weeks": 34,
        "features": {
            "rmssd": 3.0,
            "sdnn": 40.0,
            "lf_hf_ratio": 1.1,
            "sample_entropy": 1.2,
            "ac_t9": 25.0,
            "dc_t9": 22.0
        },
        "risk": {
            "predicted_class": "normal",
            "pathological": 0.05
        },
        "developmental_index": 0.75,
        "recommendations": "Continue routine monitoring"
    }

    monkeypatch.setattr(export_route, "_get_analysis_result", lambda analysis_id: analysis_result)

    transport = ASGITransport(app=app)

    async def do_request():
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.get("/api/v1/export/fhir?analysis_id=test123")

    response = asyncio.run(do_request())

    assert response.status_code == 200
    body = response.json()
    assert body["resourceType"] == "Bundle"
    assert any(entry["resource"]["resourceType"] == "Patient" for entry in body["entry"])
    assert any(entry["resource"]["resourceType"] == "Observation" for entry in body["entry"])
    assert any(entry["resource"]["resourceType"] == "DiagnosticReport" for entry in body["entry"])
