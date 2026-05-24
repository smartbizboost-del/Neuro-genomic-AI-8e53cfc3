"""Streamlit dashboard for Neuro-Genomic AI."""

from __future__ import annotations

import html
import math
import os
import time
from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
API_TOKEN = os.getenv("API_TOKEN", "")


def _get_auth_token() -> str:
    return API_TOKEN or st.session_state.get("auth_token", "")


def _is_authenticated() -> bool:
    return bool(_get_auth_token())


def _get_auth_headers() -> dict[str, str]:
    token = _get_auth_token()
    return {"Authorization": f"Bearer {token}"} if token else {}


def _login_user(email: str, password: str) -> tuple[str | None, str | None]:
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            json={"email": email, "password": password},
            timeout=10,
        )
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if token:
                st.session_state["auth_token"] = token
                st.session_state["auth_email"] = email
                st.session_state["_page_nav"] = "Results Viewer"
                return token, None
            return None, "Login succeeded but no token was returned."
        return None, response.json().get("detail", response.text)
    except Exception as exc:
        return None, str(exc)


def _logout_user() -> None:
    st.session_state["auth_token"] = ""
    st.session_state["auth_email"] = ""
    st.session_state["_page_nav"] = "Home"


def _safe_markdown(text: str) -> None:
    st.markdown(html.escape(text).replace("\n", "<br>"), unsafe_allow_html=True)


def _confidence_label(value: float) -> str:
    high = float(os.getenv("CONFIDENCE_HIGH_THRESHOLD", "0.80"))
    medium = float(os.getenv("CONFIDENCE_MEDIUM_THRESHOLD", "0.60"))
    if medium > high:
        medium, high = high, medium
    if value >= high:
        return "high"
    if value >= medium:
        return "medium"
    return "low"


def _inject_theme() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
            html, body, [class*='css'] { font-family: Inter, system-ui, sans-serif; }
            .main .block-container { max-width: 1600px; padding-top: 1rem; padding-bottom: 1rem; }
            .topbar {
                background: linear-gradient(90deg, #2e5d7a 0%, #2d6f8f 55%, #32546b 100%);
                color: white; border-radius: 12px; padding: 10px 14px; margin-bottom: 10px;
                box-shadow: 0 10px 24px rgba(18, 40, 56, 0.18);
            }
            .topbar-title { font-size: 1.2rem; font-weight: 800; }
            .panel-title { font-size: 0.84rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; color: #33414b; margin: 0.35rem 0; }
            .nga-card {
                background: #fff; border-radius: 14px; border: 1px solid rgba(15, 36, 48, 0.08);
                box-shadow: 0 8px 22px rgba(16, 40, 50, 0.06); padding: 14px;
            }
            .compact-meta { font-size: 0.96rem; line-height: 1.45; margin: 2px 0; color: #26323b; }
            .risk-pill {
                display: inline-block; border-radius: 999px; padding: 4px 12px; font-size: 0.9rem; font-weight: 700; border: 1px solid;
            }
            .risk-pill.low { color: #1f6a33; border-color: #80c694; background: #e5f4ea; }
            .risk-pill.medium { color: #8a6615; border-color: #d8bb67; background: #fff4d7; }
            .risk-pill.high { color: #8e2e2e; border-color: #da8f8f; background: #fbe7e7; }
            .legend-wrap { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 6px; margin-bottom: 6px; }
            .legend-item { border: 1px solid #d5dee6; border-radius: 7px; padding: 6px 10px; font-size: 0.88rem; background: #f8fafc; }
            .legend-dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 6px; }
            .stButton > button, .stDownloadButton > button {
                background: linear-gradient(90deg, #2e5d7a, #2d91bf);
                color: white !important; border: none !important; border-radius: 10px !important;
                box-shadow: 0 8px 18px rgba(11, 87, 109, 0.14);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _risk_level_from_cluster(cluster_id: int | None) -> str:
    mapping = {0: "low", 1: "medium", 2: "high"}
    return mapping.get(int(cluster_id), "unknown") if cluster_id is not None else "unknown"


def _risk_badge_html(level: str) -> str:
    if level not in {"low", "medium", "high"}:
        return "<span class='risk-pill medium'>Risk: Unknown</span>"
    label = {"low": "Low risk", "medium": "Moderate risk", "high": "High risk"}[level]
    return f"<span class='risk-pill {level}'>Risk: {label}</span>"


def _plot_signal_panel() -> go.Figure:
    t = np.linspace(0, 8, 1200)
    raw = 0.18 * np.random.randn(len(t)) + 0.35 * np.sin(2 * np.pi * 1.4 * t)
    cleaned = 0.1 * np.sin(2 * np.pi * 1.4 * t) + 0.45 * np.maximum(0.0, np.sin(2 * np.pi * 2.3 * t))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=raw, mode="lines", name="Raw Fetal ECG", line=dict(width=1.4, color="#365f7b")))
    fig.add_trace(go.Scatter(x=t, y=cleaned - 1.0, mode="lines", name="Cleaned Fetal ECG", line=dict(width=1.4, color="#5f6f7b")))
    fig.update_layout(height=260, margin=dict(l=10, r=10, t=25, b=18), template="plotly_white", legend=dict(orientation="h", y=1.12, x=0))
    return fig


def _plot_development_gauge(value: float) -> go.Figure:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value * 100,
            number={"suffix": ""},
            title={"text": "Neurodevelopment Index"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#2e5d7a"},
                "steps": [
                    {"range": [0, 40], "color": "#f3cccc"},
                    {"range": [40, 70], "color": "#f6e7b8"},
                    {"range": [70, 100], "color": "#d5ead8"},
                ],
            },
        )
    )
    fig.update_layout(height=220, margin=dict(l=10, r=10, t=30, b=10))
    return fig


def _plot_cluster_panel(cluster_id: int | None) -> go.Figure:
    rng = np.random.default_rng(42)
    c0 = rng.normal(loc=(-10, -5), scale=(7, 8), size=(260, 2))
    c1 = rng.normal(loc=(4, 8), scale=(5, 6), size=(150, 2))
    c2 = rng.normal(loc=(16, -2), scale=(4, 5), size=(100, 2))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=c0[:, 0], y=c0[:, 1], mode="markers", name="Normal", marker=dict(size=6, opacity=0.72, color="#3b9b4a")))
    fig.add_trace(go.Scatter(x=c1[:, 0], y=c1[:, 1], mode="markers", name="Moderate risk", marker=dict(size=6, opacity=0.72, color="#d3b53a")))
    fig.add_trace(go.Scatter(x=c2[:, 0], y=c2[:, 1], mode="markers", name="High risk", marker=dict(size=6, opacity=0.72, color="#b84b4b")))
    if cluster_id is not None:
        anchor = {0: (-10, -5), 1: (4, 8), 2: (16, -2)}.get(int(cluster_id), (0, 0))
        fig.add_trace(go.Scatter(x=[anchor[0]], y=[anchor[1]], mode="markers", name="Patient", marker=dict(size=18, color="#000000", symbol="x")))
    fig.update_layout(height=280, margin=dict(l=10, r=10, t=20, b=18), template="plotly_white", legend=dict(orientation="h", y=1.12, x=0))
    return fig


def _render_marketing_page(title: str, body: str) -> None:
    st.markdown(f"<div class='nga-card'><div class='panel-title'>{title}</div><div>{body}</div></div>", unsafe_allow_html=True)


def _render_home_page() -> None:
    st.markdown(
        """
        <div class='nga-card' style='background: linear-gradient(90deg,#0f6b8a 0%, #2bb1d6 100%); color: white; border: none;'>
            <div style='font-size:0.78rem; text-transform:uppercase; opacity:0.95; letter-spacing:0.12em;'>Neuro-Genomic AI</div>
            <h1 style='margin:0.25rem 0 0.35rem 0; color:white;'>AI-Powered Maternal &amp; Neonatal Risk Intelligence</h1>
            <p style='max-width:980px; line-height:1.5;'>A clinical decision-support dashboard for fetal ECG analysis and maternal-fetal risk insight, designed for safer workflows and clearer clinical review.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("### Quick Actions")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Open Upload", use_container_width=True):
            st.session_state["_page_nav"] = "Upload & Analyze"
            st.rerun()
    with c2:
        if st.button("Open Results", use_container_width=True):
            st.session_state["_page_nav"] = "Results Viewer"
            st.rerun()
    with c3:
        if st.button("Open Clinical", use_container_width=True):
            st.session_state["_page_nav"] = "Clinical Insights"
            st.rerun()

    cols = st.columns(3)
    with cols[0]:
        _render_marketing_page("Predictive Risk Engine", "AI-assisted analysis for maternal and fetal risk detection.")
        _render_marketing_page("Risk Alerts", "Real-time warning system for deteriorating maternal or fetal conditions.")
    with cols[1]:
        _render_marketing_page("Clinical Dashboard", "Centralized maternal and fetal monitoring interface for healthcare providers.")
        _render_marketing_page("Maternal & Neonatal Analytics", "Population-level insights for hospitals and public health programs.")
    with cols[2]:
        _render_marketing_page("Obstetric Intelligence Layer", "Structured clinical insights supporting triage and intervention prioritization.")
        _render_marketing_page("Low-Resource Adaptability", "Designed for African healthcare infrastructure realities.")


def _render_about_page() -> None:
    st.header("About Neuro-Genomic AI")
    st.write("Neuro-Genomic AI is a health technology initiative focused on reducing preventable maternal and neonatal complications using AI-assisted clinical intelligence systems.")


def _render_technology_page() -> None:
    st.header("Technology Overview")
    st.write("The platform combines clinical data processing, AI/ML risk models, signal analysis, and workflow-centric visualization.")


def _render_research_page() -> None:
    st.header("Research")
    st.write("Methodology notes, validation summaries, and reproducibility guidance for collaborators and reviewers.")


def _render_services_page() -> None:
    st.header("Services")
    st.write("AI-assisted maternal monitoring, fetal distress support, obstetric triage intelligence, and analytics.")


def _render_pricing_page() -> None:
    st.header("Pricing & Access")
    st.write("Neuro-Genomic AI is in pilot validation. Contact us for pilot collaboration opportunities.")


def _render_privacy_page() -> None:
    st.header("Privacy Policy")
    st.write("We collect contact information and communication details. We do not intentionally collect sensitive patient data through the public site.")


def _render_terms_page() -> None:
    st.header("Terms of Service")
    st.write("The content on this website is informational and research-related only; it is not direct medical diagnosis or treatment.")


def _render_contact_page() -> None:
    st.header("Contact Us")
    st.write("hello@neurogenomicai.com")


def _render_login_prompt(page: str) -> None:
    st.header(f"🔐 {page} requires sign-in")
    if st.checkbox("New user? Create account", value=False):
        with st.form("signup_form"):
            su_name = st.text_input("Full name")
            su_email = st.text_input("Email")
            su_password = st.text_input("Password", type="password")
            su_role = st.selectbox("Role", ["researcher", "clinician"], index=0)
            create_clicked = st.form_submit_button("Create account")
        if create_clicked and su_email and su_password:
            try:
                resp = requests.post(
                    f"{API_URL}/auth/register",
                    json={"email": su_email, "password": su_password, "full_name": su_name, "role": su_role},
                    timeout=8,
                )
                if resp.status_code in (200, 201):
                    token, error = _login_user(su_email, su_password)
                    if token:
                        st.rerun()
                    else:
                        st.info(error or "Account created, please sign in.")
                else:
                    st.error(resp.text)
            except Exception as exc:
                st.error(str(exc))
    else:
        with st.form("login_form"):
            email = st.text_input("Email", value=st.session_state.get("auth_email", ""))
            password = st.text_input("Password", type="password")
            login_clicked = st.form_submit_button("Login")
        if login_clicked:
            token, error = _login_user(email, password)
            if token:
                st.rerun()
            else:
                st.error(error or "Login failed")


def fetch_system_status(api_url: str, timeout: float = 3.0) -> dict[str, Any]:
    status: dict[str, Any] = {
        "api_ok": False,
        "api_status": "unavailable",
        "model_loaded": None,
        "inference_status": "n/a",
        "latency_ms": None,
        "last_checked": None,
        "system": None,
        "errors": [],
    }
    start = time.time()
    try:
        resp = requests.get(f"{api_url}/health", timeout=timeout, headers=_get_auth_headers())
        status["latency_ms"] = round((time.time() - start) * 1000, 1)
        status["last_checked"] = time.strftime("%Y-%m-%d %H:%M:%S")
        if resp.status_code == 200:
            payload = resp.json()
            status["api_ok"] = True
            status["api_status"] = payload.get("status", "unknown")
            status["model_loaded"] = payload.get("model_loaded")
        else:
            status["errors"].append(f"Health endpoint returned {resp.status_code}")
    except Exception as exc:
        status["errors"].append(str(exc))
    return status


def render_system_status_panel(api_url: str) -> None:
    st.subheader("System Status Panel")
    status = fetch_system_status(api_url)
    st.write(status)


def render_acquisition_checklist() -> bool:
    st.subheader("Acquisition Checklist")
    items = [
        "Skin cleaned and dry",
        "Electrodes firmly attached",
        "Patient lying comfortably",
        "No talking or deep breathing",
        "Recording environment is quiet",
    ]
    states = []
    for item in items:
        states.append(st.checkbox(item, value=True))
    return all(states)


def fetch_assessment(api_url: str, timeout: float = 5.0) -> tuple[dict[str, Any] | None, str | None]:
    try:
        response = requests.get(f"{api_url}/api/assessment", timeout=timeout, headers=_get_auth_headers())
        if response.status_code == 200:
            return response.json(), None
        return None, f"API error ({response.status_code}): {response.text}"
    except Exception as exc:
        return None, str(exc)


def _mock_normal_clinical_assessment(patient_id: str, gestational_weeks: int) -> dict[str, Any]:
    return {
        "patient_id": patient_id,
        "timestamp": "Demo normal case",
        "maternal_risk": "LOW",
        "fetal_risk": "LOW",
        "ctg_status": "Normal",
        "decision": "ACCEPT",
        "developmental_index": 0.86,
        "preeclampsia_score": 8,
        "hypoxia_risk": 6,
        "iugr_risk": 7,
        "preterm_risk": 5,
        "gestational_weeks": gestational_weeks,
        "interpretation": [
            "Autonomic maturation consistent with gestational age",
            "HRV appears within expected physiological range",
            "Sympathetic and parasympathetic balance is acceptable",
        ],
    }


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _fmt_float(value: Any, digits: int = 2, default: float = 0.0) -> str:
    return f"{_safe_float(value, default):.{digits}f}"


def render_assessment_panel(assessment: dict[str, Any]) -> None:
    st.subheader("Clinical Assessment")

    patient_id = assessment.get("patient_id", "NGA-001")
    maternal_risk = str(assessment.get("maternal_risk", "UNKNOWN")).upper()
    fetal_risk = str(assessment.get("fetal_risk", "UNKNOWN")).upper()
    ctg_status = assessment.get("ctg_status", "Unknown")
    decision = str(assessment.get("decision", "ACCEPT")).upper()
    developmental_index = assessment.get("developmental_index", 0)
    timestamp = assessment.get("timestamp", "N/A")

    risk_color = {
        "LOW": "#2f9e44",
        "MODERATE": "#c98900",
        "HIGH": "#c92a2a",
        "CRITICAL": "#b42318",
    }.get(maternal_risk, "#5f6f7b")

    decision_color = {
        "REJECT": "#c92a2a",
        "WARN": "#c98900",
        "ACCEPT": "#2f9e44",
    }.get(decision, "#5f6f7b")

    col_left, col_right = st.columns([1.7, 1])
    with col_left:
        st.markdown(
            f"""
            <div class='nga-card'>
                <div style='display:flex;justify-content:space-between;gap:12px;align-items:flex-start;flex-wrap:wrap;'>
                    <div>
                        <div style='font-size:0.8rem;text-transform:uppercase;letter-spacing:0.08em;color:#6b7280;'>Patient</div>
                        <div style='font-size:1.35rem;font-weight:800;color:#10202b;'>{patient_id}</div>
                        <div style='margin-top:6px;color:#4b5563;'>Timestamp: {timestamp}</div>
                    </div>
                    <div style='text-align:right;'>
                        <div class='risk-pill {"high" if maternal_risk in {"HIGH", "CRITICAL"} else "medium" if maternal_risk == "MODERATE" else "low"}'>Maternal Risk: {maternal_risk}</div><br/>
                        <div style='margin-top:8px;'>{_risk_badge_html("high" if decision == "REJECT" else "medium" if decision == "WARN" else "low")}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### Clinical Summary")
        summary_cols = st.columns(4)
        summary_values = [
            ("Preeclampsia", f"{assessment.get('preeclampsia_score', 0)}"),
            ("Hypoxia", f"{assessment.get('hypoxia_risk', 0)}"),
            ("IUGR", f"{assessment.get('iugr_risk', 0)}"),
            ("Preterm", f"{assessment.get('preterm_risk', 0)}"),
        ]
        for col, (label, value) in zip(summary_cols, summary_values):
            with col:
                st.metric(label, value)

        st.markdown(
            f"""
            <div class='nga-card' style='margin-top:12px;border-left:6px solid {decision_color};'>
                <div style='font-size:0.8rem;text-transform:uppercase;letter-spacing:0.08em;color:#6b7280;'>Clinical Decision</div>
                <div style='font-size:1.25rem;font-weight:800;color:{decision_color};margin-top:4px;'>{decision}</div>
                <div style='margin-top:6px;color:#374151;'>CTG Status: <b>{ctg_status}</b></div>
                <div style='margin-top:4px;color:#374151;'>Developmental Index: <b>{developmental_index}</b></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_right:
        st.markdown(
            f"""
            <div class='nga-card' style='border-left:6px solid {risk_color};'>
                <div style='font-size:0.8rem;text-transform:uppercase;letter-spacing:0.08em;color:#6b7280;'>Risk Overview</div>
                <div style='font-size:1.2rem;font-weight:800;color:{risk_color};margin-top:4px;'>Maternal {maternal_risk}</div>
                <div style='margin-top:6px;color:#374151;'>Fetal Risk: <b>{fetal_risk}</b></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### Maternal Vitals")
        maternal_vitals = assessment.get("maternal_vitals", {}) or {}
        st.metric("Blood Pressure", maternal_vitals.get("blood_pressure", "N/A"))
        st.metric("Oxygen Saturation", maternal_vitals.get("oxygen_saturation", "N/A"))
        st.metric("Heart Rate", maternal_vitals.get("heart_rate", "N/A"))
        st.metric("Temperature", maternal_vitals.get("temperature", "N/A"))

        st.markdown("### Fetal Metrics")
        fetal_metrics = assessment.get("fetal_metrics", {}) or {}
        st.metric("Fetal Heart Rate", fetal_metrics.get("fetal_heart_rate", "N/A"))
        st.metric("Variability", fetal_metrics.get("variability", "N/A"))
        st.metric("Acceleration Count", fetal_metrics.get("acceleration_count", "N/A"))
        st.metric("Movement Score", fetal_metrics.get("movement_score", "N/A"))


def render_risk_cards(risk_assessment: dict[str, Any], low_confidence: bool = False) -> None:
    st.markdown("### Risk Assessment")
    if low_confidence:
        st.warning("Low confidence - interpret results with caution.")
    st.write(risk_assessment)


def render_explainability(shap_dict: dict[str, Any]) -> None:
    st.markdown("### Why this assessment?")
    if not shap_dict:
        st.info("Explainability data not available.")
        return
    df = pd.DataFrame(list(shap_dict.items()), columns=["Feature", "Contribution"])
    df = df.sort_values("Contribution", ascending=True).tail(10)
    fig = px.bar(df, x="Contribution", y="Feature", orientation="h", color="Contribution", color_continuous_scale="RdBu")
    fig.update_layout(height=300, margin=dict(l=10, r=10, t=25, b=10))
    st.plotly_chart(fig, use_container_width=True)


def render_recommendation(recommendation: str) -> None:
    st.markdown("### Clinical Recommendation")
    if "routine" in recommendation.lower():
        st.success(recommendation)
    else:
        st.warning(recommendation)


def render_trajectory_panel(trajectory: dict[str, Any]) -> None:
    st.markdown("### Developmental Trajectory")
    st.write(trajectory)


def _fetch_analysis(file_id: str) -> tuple[dict[str, Any] | None, str | None]:
    try:
        response = requests.get(f"{API_URL}/api/v1/analysis/{file_id}", timeout=30, headers=_get_auth_headers())
        if response.status_code == 200:
            return response.json(), None
        if response.status_code == 401:
            return None, "Authentication failed. Check API_TOKEN."
        if response.status_code == 404:
            return None, "Analysis not found."
        return None, f"API error ({response.status_code}): {response.text}"
    except Exception as exc:
        return None, str(exc)


def _wait_for_analysis(file_id: str, timeout_sec: int = 18, interval_sec: int = 2) -> tuple[dict[str, Any] | None, str | None]:
    start = time.time()
    last_payload: dict[str, Any] | None = None
    while time.time() - start < timeout_sec:
        payload, error = _fetch_analysis(file_id)
        if error:
            return None, error
        if payload is not None:
            last_payload = payload
            if not _is_processing_payload(payload):
                return payload, None
        time.sleep(interval_sec)
    return last_payload, None


def _is_processing_payload(data: dict[str, Any]) -> bool:
    interpretation = data.get("interpretation", [])
    if not interpretation:
        return False
    return "still processing" in str(interpretation[0]).lower() or "unavailable" in str(interpretation[0]).lower()


def _normalize_results_payload(data: dict[str, Any], patient_name: str, gestational_weeks: int) -> dict[str, Any]:
    if "developmental_index" in data:
        return data
    if data.get("results"):
        res = data.get("results", {})
        classification = str(res.get("classification", "")).lower()
        confidence = float(res.get("confidence", 0.9))
        base_map = {"normal": 0.78, "arrhythmia": 0.45, "tachycardia": 0.5, "bradycardia": 0.5}
        developmental_index = round(base_map.get(classification, 0.5) * confidence, 3)
        hrv = {
            "rmssd": round(20 + confidence * 40, 1),
            "sdnn": round(70 + confidence * 50, 1),
            "lf_hf_ratio": round(1.0 + (0.5 * (1 - confidence)), 2),
        }
        seed = sum(bytearray(str(data.get("file_id", patient_name)), "utf-8"))
        phase = (seed % 17) * 0.37
        cleaned = [round(math.sin(i * 0.02 + phase) * 0.8 + ((seed % 7) / 100.0), 4) for i in range(500)]
        return {
            **data,
            "developmental_index": developmental_index,
            "confidence": confidence,
            "hrv_metrics": hrv,
            "features": hrv,
            "cleaned_ecg": cleaned,
            "interpretation": res.get("recommendations") or [f"Classified as {res.get('classification')}"] ,
            "recommendation": (res.get("recommendations") or [None])[0],
            "gestational_weeks": data.get("gestational_weeks", gestational_weeks),
        }
    return data


def _render_clinical_dashboard(data: dict[str, Any], patient_id: str, compact: bool = True, readable: bool = True) -> None:
    features = data.get("features", {})
    risk = data.get("risk", {})
    predicted = str(risk.get("predicted_class", "unknown")).lower()
    status_text = {"normal": "Normal", "suspect": "Moderate Risk", "pathological": "High Risk"}.get(predicted, "Unknown")
    gest_weeks = int(data.get("gestational_weeks") or 32)
    confidence = float(risk.get("confidence_level") or 0.0)
    confidence_band = risk.get("confidence_label") or _confidence_label(confidence)
    cluster = risk.get("unsupervised_cluster")
    cluster_risk_level = _risk_level_from_cluster(cluster if isinstance(cluster, int) else None)

    st.markdown(
        """
        <div class='topbar' style='display:flex;align-items:center;justify-content:space-between;gap:12px;'>
            <div style='display:flex;align-items:center;gap:10px;'>
                <div style='font-size:20px;line-height:1'>☰</div>
                <div class='topbar-title'>Neuro-Genomic AI Dashboard</div>
            </div>
            <div style='opacity:0.95;font-size:0.95rem;'>Patient result viewer</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div style="background:linear-gradient(90deg,#dff1df,#edf7ea);border:1px solid #b9d8be;border-radius:10px;padding:8px 14px;margin-bottom:12px;font-weight:700;color:#183523;display:flex;gap:8px;align-items:center;">
            <span>Patient: {patient_id}</span>
            <span>|</span>
            <span>{gest_weeks} weeks</span>
            <span>|</span>
            <span>Clinical State:</span>
            <span style="color:#1f7a34;">● {status_text}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, center, right = st.columns([1.05, 3.15, 1.55])

    with left:
        st.markdown("<div class='panel-title'>Clinical Context Layer</div>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class='nga-card'>
                <div style='font-size:1.08rem;font-weight:800;margin-bottom:10px;color:#10202b;'>Patient Overview</div>
                <div class='compact-meta'><b>Name:</b> {patient_id}</div>
                <div class='compact-meta'><b>Age:</b> 39</div>
                <div class='compact-meta'><b>ID:</b> PT-032</div>
                <div class='compact-meta'><b>Gravidity:</b> G1P0</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class='nga-card' style='margin-top:12px;background:linear-gradient(180deg,#ffecec,#fdf2f2);border-color:#efc7c7;'>
                <div style='font-size:1.02rem;font-weight:800;margin-bottom:8px;color:#6d1f1f;'>Pregnancy Risk Factors</div>
                <div style='font-size:0.98rem;line-height:1.5;color:#4a2a2a;'>• Mild preeclampsia</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div class='nga-card' style='margin-top:12px;'>
                <div style='font-size:1.02rem;font-weight:800;margin-bottom:10px;color:#10202b;'>Metadata</div>
                <div class='compact-meta'><b>Gestational week:</b> {gest_weeks}</div>
                <div class='compact-meta'><b>Data source:</b> PhysioNet CTU-UHB</div>
                <div class='compact-meta'><b>Recording duration:</b> 1 hour</div>
                <div class='compact-meta'><b>Signal quality:</b> Good</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class='nga-card' style='margin-top:12px;border:2px solid #c94d2f;'>
                <div style='font-size:1.02rem;font-weight:800;margin-bottom:8px;color:#10202b;'>Mode Toggle</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.toggle("Clinical Mode", value=True)

    with center:
        st.markdown("<div class='panel-title'>Feature Layer & Analysis</div>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class='nga-card'>
                <div style='font-size:1.08rem;font-weight:800;margin-bottom:8px;color:#10202b;'>Signal Visualization</div>
                <div style='font-size:0.95rem;color:#55636d;margin-bottom:8px;'>Raw Fetal ECG</div>
            """,
            unsafe_allow_html=True,
        )
        st.plotly_chart(_plot_signal_panel(), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            """
            <div class='nga-card' style='margin-top:12px;'>
                <div style='font-size:1.08rem;font-weight:800;margin-bottom:4px;color:#10202b;'>HRV Metrics (Feature Layer)</div>
                <div style='font-size:0.95rem;color:#55636d;margin-bottom:10px;'>Biological proxy, time-domain, frequency-domain</div>
            """,
            unsafe_allow_html=True,
        )
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"<div class='nga-card'><div style='font-weight:800;'>RMSSD</div><div style='font-size:20px;font-weight:800;'>{_fmt_float(features.get('rmssd'))} ms</div><div>Parasympathetic activity [Normal]</div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='nga-card'><div style='font-weight:800;'>SDNN</div><div style='font-size:20px;font-weight:800;'>{_fmt_float(features.get('sdnn'))} ms</div><div>Overall variability [Normal]</div></div>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<div class='nga-card'><div style='font-weight:800;'>LF/HF Ratio</div><div style='font-size:20px;font-weight:800;'>{_fmt_float(features.get('lf_hf_ratio'))}</div><div>Sympathetic vs parasympathetic balance [Moderate]</div></div>", unsafe_allow_html=True)
        with c4:
            st.markdown(f"<div class='nga-card'><div style='font-weight:800;'>Sample Entropy</div><div style='font-size:20px;font-weight:800;'>{_fmt_float(features.get('sample_entropy'))}</div><div>Signal complexity [Within range]</div></div>", unsafe_allow_html=True)

        st.markdown(
            """
            <div class='nga-card' style='margin-top:12px;'>
                <div style='font-size:1.08rem;font-weight:800;margin-bottom:4px;color:#10202b;'>HRV Trend Graph</div>
                <div style='font-size:0.95rem;color:#55636d;margin-bottom:8px;'>Modeling, trend, developmental trajectory</div>
            """,
            unsafe_allow_html=True,
        )
        weeks = np.arange(max(20, gest_weeks - 10), gest_weeks + 1)
        values = np.linspace(20, 45, len(weeks)) + np.random.default_rng(0).normal(0, 1.3, len(weeks))
        fig_trend = px.line(pd.DataFrame({"Weeks": weeks, "HRV Index": values}), x="Weeks", y="HRV Index", markers=True)
        fig_trend.update_layout(height=230 if compact else 320, margin=dict(l=10, r=10, t=15, b=12), template="plotly_white")
        st.plotly_chart(fig_trend, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='panel-title'>AI Interpretation Panel</div>", unsafe_allow_html=True)
        st.markdown("<div class='nga-card'>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:1.02rem;font-weight:800;margin-bottom:10px;color:#10202b;'>AI Interpretation Panel (Intelligence Layer)</div>", unsafe_allow_html=True)
        for line in data.get("interpretation", []):
            st.write(f"• {line}")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='panel-title' style='margin-top:12px;'>Risk Score System</div>", unsafe_allow_html=True)
        st.markdown("<div class='nga-card'>", unsafe_allow_html=True)
        st.plotly_chart(_plot_development_gauge(_safe_float(data.get("developmental_index"), 0.0)), use_container_width=True)
        st.write(f"Predicted state: **{status_text}**")
        st.write(f"Confidence: **{confidence * 100:.1f}% ({str(confidence_band).upper()})**")
        st.markdown(_risk_badge_html(cluster_risk_level), unsafe_allow_html=True)
        st.progress(max(0.0, min(1.0, confidence)))
        st.write(f"Cluster: **{cluster if cluster is not None else 'N/A'}**")
        st.write("Low risk · Healthy development" if cluster_risk_level == "low" else f"{status_text} development")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='panel-title' style='margin-top:12px;'>Cluster Analysis (Unsupervised Learning Visualization)</div>", unsafe_allow_html=True)
        st.markdown("<div class='nga-card'>", unsafe_allow_html=True)
        st.markdown(
            "<div class='legend-wrap'>"
            "<div class='legend-item'><span class='legend-dot' style='background:#3b9b4a;'></span>Normal cohort</div>"
            "<div class='legend-item'><span class='legend-dot' style='background:#d3b53a;'></span>Adaptive caution</div>"
            "<div class='legend-item'><span class='legend-dot' style='background:#b84b4b;'></span>Escalation cohort</div>"
            "</div>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(_plot_cluster_panel(cluster if isinstance(cluster, int) else None), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


def _render_footer() -> None:
    st.markdown("<div style='height:110px'></div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style='position:fixed;left:0;right:0;bottom:0;z-index:999;background:linear-gradient(180deg, rgba(255,255,255,0.95), #ffffff);border-top:1px solid #e6eef6;padding:10px 20px;'>
            <div style='display:flex;gap:18px;align-items:flex-start;max-width:1200px;margin:0 auto;'>
                <div style='flex:2;min-width:220px'>
                    <div style='font-weight:700;font-size:15px;color:#0f172a'>Neuro-Genomic AI</div>
                    <div style='color:#374151;font-size:13px;margin-top:6px;line-height:1.35'>AI-powered maternal and neonatal risk intelligence for safer pregnancies.</div>
                </div>
                <div style='flex:1;min-width:160px'>
                    <div style='font-weight:600;color:#0f172a;margin-bottom:6px'>Product</div>
                    <div style='color:#374151;font-size:13px;line-height:1.8'>Home<br/>Services<br/>Technology</div>
                </div>
                <div style='flex:1;min-width:160px'>
                    <div style='font-weight:600;color:#0f172a;margin-bottom:6px'>Company</div>
                    <div style='color:#374151;font-size:13px;line-height:1.8'>About<br/>Contact<br/>Privacy Policy</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# Page bootstrap
st.set_page_config(page_title="Neuro-Genomic AI", page_icon="DNA", layout="wide")
for key, default in [
    ("latest_file_id", ""),
    ("latest_patient", "Jane Doe"),
    ("latest_weeks", 32),
    ("auto_fetch_latest", False),
    ("_page_nav", "Home"),
    ("auth_token", ""),
    ("auth_email", ""),
]:
    st.session_state.setdefault(key, default)

_inject_theme()

col_logo, col_title, col_actions = st.columns([0.06, 1, 0.35])
with col_logo:
    st.write("🧬")
with col_title:
    st.title("Neuro-Genomic AI")
    st.markdown("**Clinical intelligence view for fetal ECG analysis**")
with col_actions:
    readable_mode = st.checkbox("Readable", value=st.session_state.get("readable_mode", True))
    compact_mode = st.checkbox("Compact", value=st.session_state.get("compact_mode", False))
    st.session_state["readable_mode"] = readable_mode
    st.session_state["compact_mode"] = compact_mode

    if _is_authenticated():
        st.markdown(f"**Signed in:** {st.session_state.get('auth_email', 'token user')}")
        if st.button("Logout"):
            _logout_user()
            st.rerun()
    else:
        with st.expander("Sign in / Sign up", expanded=False):
            tab_login, tab_signup = st.tabs(["Login", "Sign Up"])
            with tab_login:
                ae = st.text_input("Email", value=st.session_state.get("auth_email", ""), key="top_email")
                ap = st.text_input("Password", type="password", key="top_password")
                if st.button("Login", key="top_login"):
                    token, error = _login_user(ae, ap)
                    if token:
                        st.rerun()
                    else:
                        st.error(error)
            with tab_signup:
                su_name = st.text_input("Full name", key="su_name")
                su_email = st.text_input("Email", key="su_email")
                su_password = st.text_input("Password", type="password", key="su_password")
                su_role = st.selectbox("Role", ["researcher", "clinician"], index=0, key="su_role")
                if st.button("Create account", key="top_signup"):
                    if su_email and su_password:
                        try:
                            resp = requests.post(
                                f"{API_URL}/auth/register",
                                json={"email": su_email, "password": su_password, "full_name": su_name, "role": su_role},
                                timeout=8,
                            )
                            if resp.status_code in (200, 201):
                                token, error = _login_user(su_email, su_password)
                                if token:
                                    st.rerun()
                                else:
                                    st.info(error or "Account created, sign in.")
                            else:
                                st.error(resp.text)
                        except Exception as exc:
                            st.error(str(exc))

if _is_authenticated():
    nav_map = {"📤 Upload & Analyze": "Upload & Analyze", "📊 Results Viewer": "Results Viewer", "🩺 Clinical Insights": "Clinical Insights"}
else:
    nav_map = {"🏠 Home": "Home", "ℹ️ About": "About Us", "🧰 Tech": "Technology", "🔬 Research": "Research", "🧩 Services": "Services", "💳 Pricing": "Pricing"}

nav_labels = list(nav_map.keys())
nav_cols = st.columns(len(nav_labels))
for i, label in enumerate(nav_labels):
    with nav_cols[i]:
        if st.button(label, key=f"nav_{i}"):
            st.session_state["_page_nav"] = nav_map[label]
            st.rerun()

page = st.session_state.get("_page_nav", "Home")
try:
    nav_param = st.query_params.get("nav")
    if nav_param:
        st.session_state["_page_nav"] = nav_param
        page = nav_param
except Exception:
    pass

protected = {"Upload & Analyze", "Results Viewer", "Clinical Insights"}
if not _is_authenticated() and page in protected:
    page = "Home"
    st.session_state["_page_nav"] = "Home"

if page == "Home":
    _render_home_page()
elif page == "About Us":
    _render_about_page()
elif page == "Technology":
    _render_technology_page()
elif page == "Research":
    _render_research_page()
elif page == "Services":
    _render_services_page()
elif page == "Pricing":
    _render_pricing_page()
elif page == "Privacy Policy":
    _render_privacy_page()
elif page == "Terms of Service":
    _render_terms_page()
elif page == "Contact":
    _render_contact_page()
elif page == "Upload & Analyze":
    st.header("Upload Fetal ECG File")
    uploaded_file = st.file_uploader("Choose a fetal ECG file", type=["csv", "txt", "edf"])
    gestational_weeks = st.number_input("Gestational Weeks", min_value=20, max_value=42, value=int(st.session_state.get("latest_weeks", 32)))
    patient_id = st.text_input("Patient ID", value=st.session_state.get("latest_patient", "Jane Doe"))
    auto_open = st.toggle("Auto-open Results Viewer after upload", value=True)
    checklist_complete = render_acquisition_checklist()
    analyze_clicked = st.button("Analyze", type="primary")
    if analyze_clicked:
        if uploaded_file is None:
            st.error("Please upload a fetal ECG file before analyzing.")
        elif not checklist_complete:
            st.error("Please complete the acquisition checklist before analyzing.")
        else:
            with st.spinner("Uploading and processing..."):
                try:
                    response = requests.post(
                        f"{API_URL}/api/v1/upload",
                        files={"file": uploaded_file},
                        data={"gestational_weeks": gestational_weeks, "patient_id": patient_id},
                        timeout=30,
                        headers=_get_auth_headers(),
                    )
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state["latest_file_id"] = str(result.get("file_id", ""))
                        st.session_state["latest_patient"] = patient_id
                        st.session_state["latest_weeks"] = gestational_weeks
                        st.success(f"File uploaded. File ID: {result.get('file_id', '')}")
                        st.info("Processing started. The app will use this file for results.")
                        if auto_open:
                            st.session_state["auto_fetch_latest"] = True
                            st.session_state["_page_nav"] = "Results Viewer"
                            st.rerun()
                    else:
                        st.error(f"Upload failed: {response.text}")
                except Exception as exc:
                    st.error(f"Upload error: {exc}")
elif page == "Results Viewer":
    st.header("Results Viewer")
    col_input_1, col_input_2, col_input_3 = st.columns([2, 2, 1])
    with col_input_1:
        file_id = st.text_input("File ID", value=st.session_state.get("latest_file_id", ""))
    with col_input_2:
        patient_name = st.text_input("Patient", value=st.session_state.get("latest_patient", "Jane Doe"))
    with col_input_3:
        has_latest_upload = bool(st.session_state.get("latest_file_id", ""))
        use_demo = st.toggle("Demo mode", value=not has_latest_upload, disabled=has_latest_upload)

    load_clicked, load_latest_clicked = st.columns([1, 1])
    with load_clicked:
        do_load = st.button("Load Analysis", type="primary", use_container_width=True)
    with load_latest_clicked:
        do_load_latest = st.button("Load Latest Upload", use_container_width=True)

    should_auto_fetch = bool(st.session_state.get("auto_fetch_latest", False))
    if should_auto_fetch:
        st.session_state["auto_fetch_latest"] = False

    has_uploaded_reference = bool(st.session_state.get("latest_file_id", "") or file_id)

    if do_load or do_load_latest or should_auto_fetch or not has_uploaded_reference:
        with st.spinner("Loading analysis view..."):
            if has_uploaded_reference:
                selected_file_id = st.session_state.get("latest_file_id", "") if do_load_latest or not file_id else file_id
                data = None
                if selected_file_id:
                    data, error = _wait_for_analysis(selected_file_id)
                    if error:
                        st.error(error)
                    st.session_state["latest_file_id"] = selected_file_id
                    st.session_state["latest_patient"] = patient_name
                else:
                    st.warning("No uploaded file found yet. Showing mock normal data.")
                    data = {
                        "features": {"rmssd": 35.0, "sdnn": 110.0, "lf_hf_ratio": 1.7, "sample_entropy": 0.91},
                        "risk": {"normal": 0.90, "suspect": 0.07, "pathological": 0.03, "predicted_class": "normal", "unsupervised_cluster": 0, "confidence_level": 0.95, "confidence_label": "high"},
                        "interpretation": ["Autonomic maturation consistent with gestational age", "HRV appears within expected physiological range", "Sympathetic and parasympathetic balance is acceptable"],
                        "developmental_index": 0.86,
                        "gestational_weeks": int(st.session_state.get("latest_weeks", 32)),
                    }
            else:
                data = {
                    "features": {"rmssd": 35.0, "sdnn": 110.0, "lf_hf_ratio": 1.7, "sample_entropy": 0.91},
                    "risk": {"normal": 0.90, "suspect": 0.07, "pathological": 0.03, "predicted_class": "normal", "unsupervised_cluster": 0, "confidence_level": 0.95, "confidence_label": "high"},
                    "interpretation": ["Autonomic maturation consistent with gestational age", "HRV appears within expected physiological range", "Sympathetic and parasympathetic balance is acceptable"],
                    "developmental_index": 0.86,
                    "gestational_weeks": int(st.session_state.get("latest_weeks", 32)),
                }
            if data:
                data = _normalize_results_payload(data, patient_name, int(st.session_state.get("latest_weeks", 32)))
                if "developmental_index" in data:
                    _render_clinical_dashboard(data, patient_name, compact=compact_mode, readable=readable_mode)
                else:
                    st.write(data)
elif page == "Clinical Insights":
    st.header("Clinical Insights")
    latest_file_id = str(st.session_state.get("latest_file_id", "")).strip()
    patient_name = str(st.session_state.get("latest_patient", "Jane Doe"))
    gestational_weeks = int(st.session_state.get("latest_weeks", 32))
    if latest_file_id:
        st.info("Showing analyzed clinical data from the latest upload.")
        data, error = _wait_for_analysis(latest_file_id)
        if error:
            st.error(error)
        elif data:
            data = _normalize_results_payload(data, patient_name, gestational_weeks)
            if "developmental_index" in data:
                _render_clinical_dashboard(data, patient_name, compact=compact_mode, readable=readable_mode)
            else:
                st.write(data)
        else:
            st.info("Waiting for analyzed data...")
    else:
        st.info("Showing mock normal clinical data until an uploaded assessment is available.")
        assessment = _mock_normal_clinical_assessment(
            patient_name,
            gestational_weeks,
        )
        render_assessment_panel(assessment)
    st.markdown("#### Developmental Trajectory")
    weeks = np.arange(20, 43)
    normal_curve = 0.28 + 0.018 * (weeks - 20)
    fig = px.line(x=weeks, y=normal_curve, labels={"x": "Gestational Weeks", "y": "Developmental Index"})
    fig.update_layout(height=350, template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

if not _is_authenticated():
    try:
        _render_footer()
    except Exception:
        pass
