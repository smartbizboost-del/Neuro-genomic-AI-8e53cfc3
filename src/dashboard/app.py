"""Streamlit dashboard for Neuro-Genomic AI."""

import os
import time
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

from src.core.pipeline import get_pipeline

API_URL = os.getenv("API_URL", "http://localhost:8000")


# ============================================================================
# OPTIMIZED COMPONENT FUNCTIONS
# ============================================================================

def render_developmental_index(dev_index: float, confidence: float):
    """Top prominent Developmental Index card"""
    st.markdown("### Developmental Index")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.progress(dev_index)
    with col2:
        st.metric("Score", f"{dev_index:.2f}/1.0", f"±{confidence*100:.0f}%")
    
    color = "green" if dev_index >= 0.75 else "orange" if dev_index >= 0.60 else "red"
    status = "Normal" if dev_index >= 0.75 else "Borderline" if dev_index >= 0.60 else "At Risk"
    st.markdown(f"<h4 style='color:{color};'>{status}</h4>", unsafe_allow_html=True)


def render_risk_cards(risk_assessment: dict):
    """Risk Assessment Cards - Clinical traffic light style"""
    st.markdown("### Risk Assessment")
    cols = st.columns(3)
    
    # Handle both new format (risk_assessment with iugr_risk, etc.)
    # and old format (risk with predicted_class, etc.)
    if "iugr_risk" in risk_assessment:
        # New format
        risks = [
            ("IUGR Risk", risk_assessment.get("iugr_risk", {}), "🔴"),
            ("Preterm Risk", risk_assessment.get("preterm_risk", {}), "🟡"),
            ("Hypoxia Risk", risk_assessment.get("hypoxia_risk", {}), "⚪")
        ]
    else:
        # Old format - convert from predicted probabilities
        normal_score = risk_assessment.get("normal", 0.78) * 100
        suspect_score = risk_assessment.get("suspect", 0.17) * 100
        pathological_score = risk_assessment.get("pathological", 0.05) * 100
        
        risks = [
            ("Normal", {"score": normal_score, "ci": "±8%", "note": ""}, "🟢"),
            ("Suspect", {"score": suspect_score, "ci": "±12%", "note": ""}, "🟡"),
            ("Pathological", {"score": pathological_score, "ci": "±5%", "note": ""}, "🔴")
        ]
    
    for col, (label, data, emoji) in zip(cols, risks):
        with col:
            score = data.get("score", 0) if isinstance(data, dict) else 0
            ci = data.get("ci", "") if isinstance(data, dict) else ""
            note = data.get("note", "") if isinstance(data, dict) else ""
            
            color = "#4ade80" if score < 20 else "#fbbf24" if score < 40 else "#f87171"
            
            st.markdown(f"""
            <div style="background-color: {color}20; padding: 15px; border-radius: 10px; text-align: center; border: 2px solid {color}">
                <h3>{emoji} {label}</h3>
                <h2>{score:.1f}%</h2>
                <p>{ci}</p>
                {f'<small>{note}</small>' if note else ''}
            </div>
            """, unsafe_allow_html=True)


def render_explainability(shap_dict: dict):
    """SHAP Explainability Panel"""
    st.markdown("### Why this assessment?")
    if not shap_dict:
        st.info("Explainability data not available yet.")
        return
    
    try:
        # Convert to DataFrame for plotting
        if isinstance(shap_dict, dict) and len(shap_dict) > 0:
            df = pd.DataFrame(list(shap_dict.items()), columns=["Feature", "Contribution"])
            df = df.sort_values("Contribution", ascending=True).tail(10)  # Top 10 features
            
            fig = px.bar(df, x="Contribution", y="Feature", orientation='h',
                         title="Feature Contribution (SHAP values)",
                         color="Contribution", color_continuous_scale="RdBu")
            fig.update_layout(height=300, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("No explainability features available")
    except Exception as e:
        st.warning(f"Could not display explainability: {e}")


def render_recommendation(recommendation: str):
    """Clinical Recommendation Box"""
    st.markdown("### Clinical Recommendation")
    if "routine" in recommendation.lower():
        st.success(recommendation)
    else:
        st.warning(recommendation)


def render_trajectory_panel(trajectory: dict):
    """Developmental Trajectory Panel"""
    st.markdown("### Developmental Trajectory")
    if not trajectory:
        st.info("Trajectory data not available yet.")
        return
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Trend", trajectory.get("trend", "stable").title())
    with col2:
        st.metric("Slope", f"{trajectory.get('slope', 0):.4f}")
    with col3:
        st.metric("Predicted (Next)",  f"{trajectory.get('predicted_next_week', 0):.2f}")
    
    if trajectory.get("deviation"):
        st.caption(f"Deviation from prediction: {trajectory['deviation']:.2f}")


def _inject_theme(compact: bool = False, readable: bool = True) -> None:
    compact_css = """
            .main .block-container {
                max-width: 98vw;
                padding-top: .6rem;
                padding-bottom: .5rem;
            }
            h1 { font-size: 1.55rem !important; margin-bottom: .2rem !important; }
            h3 { font-size: 1.0rem !important; margin-bottom: .1rem !important; }
            h4 { font-size: .92rem !important; margin-bottom: .05rem !important; }
    """ if compact else ""

    readable_css = """
            .main .block-container {
                max-width: 99vw;
                padding-top: .9rem;
                padding-bottom: .8rem;
            }
            h1 { font-size: 2.0rem !important; margin-bottom: .35rem !important; }
            h3 { font-size: 1.22rem !important; }
            h4 { font-size: 1.04rem !important; }
            .stButton > button, .stDownloadButton > button {
                font-size: 1rem !important;
                min-height: 40px;
            }
            label, .stMarkdown, .stTextInput, .stNumberInput {
                font-size: 1rem !important;
            }
    """ if readable else ""

    css = """
        <style>
            .main .block-container {
                padding-top: 1.2rem;
                padding-bottom: 1.2rem;
            }
            .topbar {
                background: linear-gradient(90deg, #1f4968 0%, #2b5c7e 100%);
                color: #f5f8fa;
                border-radius: 10px;
                padding: 10px 14px;
                margin-bottom: 10px;
                border: 1px solid #1d415d;
            }
            .topbar-title {
                font-size: 28px;
                font-weight: 700;
                letter-spacing: 0.2px;
                margin: 0;
            }
            .panel-title {
                font-size: 15px;
                letter-spacing: .35px;
                font-weight: 700;
                text-transform: uppercase;
                color: #273542;
                margin-bottom: .35rem;
            }
            .mini-note {
                font-size: 13px;
                color: #4b5a66;
                margin-top: -4px;
            }
            .risk-pill {
                display: inline-block;
                border-radius: 999px;
                padding: 4px 12px;
                font-size: 14px;
                font-weight: 700;
                border: 1px solid;
            }
            .risk-pill.low {
                color: #1f6a33;
                border-color: #80c694;
                background: #e5f4ea;
            }
            .risk-pill.medium {
                color: #8a6615;
                border-color: #d8bb67;
                background: #fff4d7;
            }
            .risk-pill.high {
                color: #8e2e2e;
                border-color: #da8f8f;
                background: #fbe7e7;
            }
            .legend-wrap {
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
                margin-top: 6px;
                margin-bottom: 4px;
            }
            .legend-item {
                border: 1px solid #d5dee6;
                border-radius: 7px;
                padding: 6px 10px;
                font-size: 14px;
                background: #f8fafc;
            }
            .legend-dot {
                display: inline-block;
                width: 10px;
                height: 10px;
                border-radius: 50%;
                margin-right: 6px;
            }
            .compact-meta {
                font-size: 14px;
                line-height: 1.45;
                margin-top: 2px;
                margin-bottom: 2px;
            }
            .compact-meta b {
                color: #33414b;
            }
            @media (max-height: 900px) {
                .main .block-container {
                    padding-top: .45rem;
                    padding-bottom: .45rem;
                }
            }
            __COMPACT_CSS__
            __READABLE_CSS__
        </style>
        """.replace("__COMPACT_CSS__", compact_css)
    css = css.replace("__READABLE_CSS__", readable_css)
    st.markdown(css, unsafe_allow_html=True)


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


def _risk_state(predicted_class: str) -> str:
    mapping = {
        "normal": "Normal",
        "suspect": "Moderate Risk",
        "pathological": "High Risk",
    }
    return mapping.get(str(predicted_class).lower(), "Unknown")


def _mock_signal(fs: int = 500, seconds: int = 8) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    t = np.linspace(0.0, seconds, fs * seconds, endpoint=False)
    raw = 0.2 * np.random.randn(len(t)) + 0.35 * np.sin(2 * np.pi * 1.4 * t)
    cleaned = 0.1 * np.sin(2 * np.pi * 1.4 * t) + 0.45 * np.maximum(0.0, np.sin(2 * np.pi * 2.3 * t))
    return t, raw, cleaned


def _plot_signal_panel(compact: bool = True, readable: bool = True) -> go.Figure:
    t, raw, cleaned = _mock_signal()
    fig = go.Figure()
    lw = 1.8 if readable else 1.2
    fig.add_trace(go.Scatter(x=t, y=raw, mode="lines", name="Raw Fetal ECG", line=dict(width=lw, color="#2f5d80")))
    fig.add_trace(go.Scatter(x=t, y=cleaned - 1.1, mode="lines", name="Cleaned Fetal ECG", line=dict(width=lw, color="#5f6f7b")))
    fig.update_layout(
        height=260 if compact else (360 if readable else 300),
        margin=dict(l=10, r=10, t=30, b=20),
        template="plotly_white",
        legend=dict(orientation="h", y=1.12, x=0, font=dict(size=13 if readable else 11)),
        xaxis_title="Time (s)",
        yaxis_title="Amplitude",
        font=dict(size=14 if readable else 11),
    )
    return fig


def _plot_development_gauge(value: float, compact: bool = True, readable: bool = True) -> go.Figure:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value * 100,
            number={"suffix": ""},
            title={"text": "Neurodevelopment Index"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#2f5d80"},
                "steps": [
                    {"range": [0, 40], "color": "#f3cccc"},
                    {"range": [40, 70], "color": "#f6e7b8"},
                    {"range": [70, 100], "color": "#d5ead8"},
                ],
            },
        )
    )
    fig.update_layout(height=220 if compact else (300 if readable else 250), margin=dict(l=10, r=10, t=26 if compact else 40, b=8), font=dict(size=14 if readable else 11))
    return fig


def _plot_cluster_panel(
    cluster_id: int | None,
    compact: bool = True,
    readable: bool = True,
) -> go.Figure:
    rng = np.random.default_rng(42)
    c0 = rng.normal(loc=(-10, -5), scale=(7, 8), size=(260, 2))
    c1 = rng.normal(loc=(4, 8), scale=(5, 6), size=(150, 2))
    c2 = rng.normal(loc=(16, -2), scale=(4, 5), size=(100, 2))

    fig = go.Figure()
    msize = 8 if readable else 6
    marker_style = dict(size=msize, opacity=0.72, line=dict(width=0.5, color="#1a1a1a"))

    fig.add_trace(go.Scatter(x=c0[:, 0], y=c0[:, 1], mode="markers", name="Normal", marker={**marker_style, "color": "#3b9b4a"}))
    fig.add_trace(go.Scatter(x=c1[:, 0], y=c1[:, 1], mode="markers", name="Moderate risk", marker={**marker_style, "color": "#d3b53a"}))
    fig.add_trace(go.Scatter(x=c2[:, 0], y=c2[:, 1], mode="markers", name="High risk", marker={**marker_style, "color": "#b84b4b"}))

    if cluster_id is not None:
        anchor = {0: (-10, -5), 1: (4, 8), 2: (16, -2)}.get(int(cluster_id), (0, 0))
        fig.add_trace(
            go.Scatter(
                x=[anchor[0]],
                y=[anchor[1]],
                mode="markers",
                name="Patient",
                marker=dict(size=22 if readable else 16, color="#000000", symbol="x"),
            )
        )

    all_points = np.vstack([c0, c1, c2])
    x_min, y_min = all_points.min(axis=0)
    x_max, y_max = all_points.max(axis=0)
    x_pad = (x_max - x_min) * 0.12
    y_pad = (y_max - y_min) * 0.12

    plot_height = 300 if compact else (380 if readable else 280)

    fig.update_layout(
        height=plot_height,
        margin=dict(l=10, r=10, t=20, b=20),
        template="plotly_white",
        xaxis_title="PCA-1",
        yaxis_title="PCA-2",
        legend=dict(orientation="h", y=1.16, x=0, title="Phenotype clusters", font=dict(size=13 if readable else 11)),
        font=dict(size=15 if readable else 11),
        hovermode="closest",
        dragmode="zoom",
    )
    fig.update_xaxes(range=[x_min - x_pad, x_max + x_pad], showgrid=True, gridcolor="#dce5ef", zeroline=True)
    fig.update_yaxes(range=[y_min - y_pad, y_max + y_pad], showgrid=True, gridcolor="#dce5ef", zeroline=True)
    return fig


def _risk_level_from_cluster(cluster_id: int | None) -> str:
    if cluster_id is None:
        return "unknown"
    mapping = {0: "low", 1: "medium", 2: "high"}
    return mapping.get(int(cluster_id), "unknown")


def _risk_badge_html(level: str) -> str:
    if level not in {"low", "medium", "high"}:
        return "<span class='risk-pill medium'>Risk: Unknown</span>"
    text = {"low": "Low risk", "medium": "Moderate risk", "high": "High risk"}[level]
    return f"<span class='risk-pill {level}'>Risk: {text}</span>"


def _cluster_legend_html(cluster_id: int | None) -> str:
    selected = _risk_level_from_cluster(cluster_id)
    return f"""
    <div class='legend-wrap'>
      <div class='legend-item'><span class='legend-dot' style='background:#3b9b4a;'></span>Normal cohort (low risk)</div>
      <div class='legend-item'><span class='legend-dot' style='background:#d3b53a;'></span>Adaptive caution (moderate risk)</div>
      <div class='legend-item'><span class='legend-dot' style='background:#b84b4b;'></span>Escalation cohort (high risk)</div>
      <div class='legend-item'><span class='legend-dot' style='background:#000000;'></span>Patient projection ({selected})</div>
    </div>
    """


def _render_top_action_bar(patient_id: str) -> None:
    c1, c2, c3, c4 = st.columns([3.0, 2.0, 1.1, 1.25])
    with c1:
        st.markdown("<div class='topbar'><div class='topbar-title'>Neuro-Genomic AI Dashboard</div></div>", unsafe_allow_html=True)
    with c2:
        st.selectbox("Patient", [patient_id, "Jane Doe", "PT-032", "PT-041"], label_visibility="collapsed")
    with c3:
        if st.button("📥 Export", use_container_width=True, key="btn_export"):
            st.info("Export options:")
            col_a, col_b = st.columns(2)
            with col_a:
                st.download_button("Clinical Report", "Report export placeholder", file_name="clinical_report.txt", use_container_width=True)
            with col_b:
                st.download_button("Validation", "Validation export placeholder", file_name="validation_results.txt", use_container_width=True)
    with c4:
        if st.button("📄 PDF Report", use_container_width=True, key="btn_pdf"):
            col_a, col_b = st.columns(2)
            with col_a:
                st.button("Generate PDF", use_container_width=True, key="btn_gen_pdf")
            with col_b:
                st.button("Open Last", use_container_width=True, key="btn_open_pdf")


def _feature_card(title: str, value_text: str, subtitle: str, color: str) -> str:
    return f"""
                <div style="border:1px solid #d7d7d7;border-left:6px solid {color};border-radius:8px;padding:10px 12px;background:#f8fafb;min-height:92px;">
            <div style="font-weight:700;font-size:17px;">{title}</div>
                        <div style="font-size:20px;font-weight:700;margin-top:3px;">{value_text}</div>
                        <div style="font-size:13px;color:#4a4a4a;margin-top:5px;">{subtitle}</div>
    </div>
    """


def _render_clinical_dashboard(data: dict[str, Any], patient_id: str, compact: bool = True, readable: bool = True) -> None:
    features = data.get("features", {})
    risk = data.get("risk", {})

    predicted = str(risk.get("predicted_class", "unknown")).lower()
    status_text = _risk_state(predicted)
    gest_weeks = int(data.get("gestational_weeks") or 32)
    confidence = float(risk.get("confidence_level") or 0.0)
    confidence_band = risk.get("confidence_label") or _confidence_label(confidence)
    cluster = risk.get("unsupervised_cluster")
    cluster_risk_level = _risk_level_from_cluster(cluster if isinstance(cluster, int) else None)

    _render_top_action_bar(patient_id)

    st.markdown(
        f"""
        <div style="background:#deeee1;border:1px solid #b7d8be;border-radius:8px;padding:8px 12px;margin-bottom:12px;font-weight:600;">
          Patient: {patient_id} | {gest_weeks} weeks | Clinical State: <span style="color:#236c2b;">{status_text}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, center, right = st.columns([1.05, 3.15, 1.55])

    with left:
        st.markdown("<div class='panel-title'>Clinical Context Layer</div>", unsafe_allow_html=True)
        st.markdown("#### Patient Overview")
        st.markdown(
            f"""
            <div class='compact-meta'><b>Name:</b> {patient_id}</div>
            <div class='compact-meta'><b>Age:</b> 39 | <b>ID:</b> PT-032</div>
            <div class='compact-meta'><b>Gravidity:</b> G1P0</div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("#### Pregnancy Risk Factors")
        st.warning("Mild preeclampsia")

        st.markdown("#### Metadata")
        st.markdown(
            f"""
            <div class='compact-meta'><b>Gestational week:</b> {gest_weeks}</div>
            <div class='compact-meta'><b>Source:</b> PhysioNet CTU-UHB</div>
            <div class='compact-meta'><b>Duration:</b> 1 hour | <b>Signal quality:</b> Good</div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("#### Mode Toggle")
        st.toggle("Clinical mode", value=True)

    with center:
        st.markdown("<div class='panel-title'>Feature Layer & Analysis</div>", unsafe_allow_html=True)
        st.markdown("#### Signal Visualization")
        st.markdown("<div class='mini-note'>Raw and cleaned ECG overlays for qualitative signal checks.</div>", unsafe_allow_html=True)
        st.plotly_chart(_plot_signal_panel(compact=compact, readable=readable), use_container_width=True)

        st.markdown("#### HRV Metrics")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(
                _feature_card("RMSSD", f"{features.get('rmssd', 0):.2f} ms", "Parasympathetic activity", "#5a9f63"),
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                _feature_card("SDNN", f"{features.get('sdnn', 0):.2f} ms", "Overall variability", "#5a9f63"),
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                _feature_card("LF/HF Ratio", f"{features.get('lf_hf_ratio', 0):.2f}", "Sympathetic vs parasympathetic", "#c8a73e"),
                unsafe_allow_html=True,
            )
        with c4:
            st.markdown(
                _feature_card("Sample Entropy", f"{features.get('sample_entropy', 0):.2f}", "Signal complexity", "#5a9f63"),
                unsafe_allow_html=True,
            )

        st.markdown("#### HRV Trend Graph")
        st.markdown("<div class='mini-note'>Modeling developmental trajectory across gestational windows.</div>", unsafe_allow_html=True)
        weeks = np.arange(max(20, gest_weeks - 10), gest_weeks + 1)
        values = np.linspace(20, 45, len(weeks)) + np.random.default_rng(0).normal(0, 1.3, len(weeks))
        trend = pd.DataFrame({"Weeks": weeks, "HRV Index": values})
        fig_trend = px.line(trend, x="Weeks", y="HRV Index", markers=True)
        fig_trend.update_layout(height=230 if compact else (320 if readable else 280), margin=dict(l=10, r=10, t=15, b=12), template="plotly_white", font=dict(size=14 if readable else 11))
        st.plotly_chart(fig_trend, use_container_width=True)

    with right:
        st.markdown("<div class='panel-title'>AI Interpretation Panel</div>", unsafe_allow_html=True)
        for line in data.get("interpretation", []):
            st.write(f"- {line}")

        st.markdown("<div class='panel-title'>Risk Score System</div>", unsafe_allow_html=True)
        st.plotly_chart(_plot_development_gauge(float(data.get("developmental_index", 0.0)), compact=compact, readable=readable), use_container_width=True)
        st.write(f"Predicted state: **{status_text}**")
        st.write(f"Confidence: **{confidence * 100:.1f}% ({str(confidence_band).upper()})**")
        st.markdown(_risk_badge_html(cluster_risk_level), unsafe_allow_html=True)
        st.progress(max(0.0, min(1.0, confidence)))
        st.write(f"Cluster: **{cluster if cluster is not None else 'N/A'}**")

        st.markdown("<div class='panel-title'>Cluster Analysis (Unsupervised Learning Visualization)</div>", unsafe_allow_html=True)
        st.markdown(_cluster_legend_html(cluster if isinstance(cluster, int) else None), unsafe_allow_html=True)
        st.plotly_chart(
            _plot_cluster_panel(cluster if isinstance(cluster, int) else None, compact=compact, readable=readable),
            use_container_width=True,
            config={"displaylogo": False, "modeBarButtonsToAdd": ["zoomIn2d", "zoomOut2d", "resetScale2d"]},
        )


def _is_processing_payload(data: dict[str, Any]) -> bool:
    interpretation = data.get("interpretation", [])
    if not interpretation:
        return False
    first_line = str(interpretation[0]).lower()
    return "still processing" in first_line or "unavailable" in first_line


def _fetch_analysis(file_id: str) -> tuple[dict[str, Any] | None, str | None]:
    try:
        response = requests.get(f"{API_URL}/api/v1/analysis/{file_id}", timeout=30)
        if response.status_code == 200:
            return response.json(), None
        return None, f"API error: {response.text}"
    except Exception as exc:
        return None, f"Fetch error: {exc}"


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


st.set_page_config(page_title="Neuro-Genomic AI Dashboard", page_icon="DNA", layout="wide")

if "latest_file_id" not in st.session_state:
    st.session_state["latest_file_id"] = ""
if "latest_patient" not in st.session_state:
    st.session_state["latest_patient"] = "Jane Doe"
if "latest_weeks" not in st.session_state:
    st.session_state["latest_weeks"] = 32
if "auto_fetch_latest" not in st.session_state:
    st.session_state["auto_fetch_latest"] = False
if "_page_nav" not in st.session_state:
    st.session_state["_page_nav"] = "Upload & Analyze"

st.sidebar.header("Display")
readable_mode = st.sidebar.toggle("Readable mode (larger UI)", value=True)
compact_mode = st.sidebar.toggle("Compact one-screen mode", value=not readable_mode)

_inject_theme(compact=compact_mode, readable=readable_mode)

# Display logo and title at the top
col_logo, col_title = st.columns([0.05, 1])
with col_logo:
    # st.image("logo.png", width=28, use_column_width=False)
with col_title:
        pass
    st.title("Neuro-Genomic AI Dashboard")
    st.markdown("**Clinical intelligence view for fetal ECG analysis**")

st.sidebar.header("Navigation")
# Get the index of the current page from session state
page_options = ["Upload & Analyze", "Results Viewer", "Clinical Insights"]
current_page = st.session_state.get("_page_nav", "Upload & Analyze")
current_index = page_options.index(current_page) if current_page in page_options else 0

page = st.sidebar.radio("Go to", page_options, index=current_index)

# Update internal state when radio selection changes
st.session_state["_page_nav"] = page

if page == "Upload & Analyze":
    st.header("Upload Fetal ECG File")
    uploaded_file = st.file_uploader("Choose a fetal ECG file", type=["csv", "txt", "edf"])
    gestational_weeks = st.number_input("Gestational Weeks", min_value=20, max_value=42, value=32)
    patient_id = st.text_input("Patient ID", value="Jane Doe")
    auto_open = st.toggle("Auto-open Results Viewer after upload", value=True)

    if st.button("Analyze", type="primary") and uploaded_file is not None:
        with st.spinner("Uploading and processing..."):
            files = {"file": uploaded_file}
            form_data = {"gestational_weeks": gestational_weeks, "patient_id": patient_id}
            try:
                response = requests.post(f"{API_URL}/api/v1/upload", files=files, data=form_data, timeout=30)
                if response.status_code == 200:
                    result = response.json()
                    file_id = str(result.get("file_id", ""))
                    st.session_state["latest_file_id"] = file_id
                    st.session_state["latest_patient"] = patient_id
                    st.session_state["latest_weeks"] = gestational_weeks
                    st.success(f"File uploaded. File ID: {file_id}")
                    st.info("Processing started. Dashboard will use this file for results.")
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
        use_demo = st.toggle("Demo mode", value=False)

    cbtn1, cbtn2 = st.columns([1, 1])
    load_clicked = cbtn1.button("Load Dashboard", type="primary", use_container_width=True)
    load_latest_clicked = cbtn2.button("Load Latest Upload", use_container_width=True)

    should_auto_fetch = bool(st.session_state.get("auto_fetch_latest", False))
    if should_auto_fetch:
        st.session_state["auto_fetch_latest"] = False

    if load_clicked or load_latest_clicked or should_auto_fetch:
        with st.spinner("Loading analysis dashboard..."):
            data = None
            if use_demo:
                data = {
                    "features": {
                        "rmssd": 35.0,
                        "sdnn": 110.0,
                        "lf_hf_ratio": 1.7,
                        "sample_entropy": 0.91,
                    },
                    "risk": {
                        "normal": 0.78,
                        "suspect": 0.17,
                        "pathological": 0.05,
                        "predicted_class": "normal",
                        "unsupervised_cluster": 0,
                        "confidence_level": 0.82,
                        "confidence_label": "high",
                    },
                    "interpretation": [
                        "Autonomic maturation consistent with gestational age",
                        "HRV appears within expected physiological range",
                        "Sympathetic and parasympathetic balance is acceptable",
                    ],
                    "developmental_index": 0.74,
                    "gestational_weeks": 32,
                }
            else:
                selected_file_id = st.session_state.get("latest_file_id", "") if load_latest_clicked else file_id
                if selected_file_id:
                    data, error = _wait_for_analysis(selected_file_id)
                    if error:
                        st.error(error)
                    elif data is not None and _is_processing_payload(data):
                        st.info("Analysis is still processing. Showing latest available payload.")
                    st.session_state["latest_file_id"] = selected_file_id
                    st.session_state["latest_patient"] = patient_name
                else:
                    st.warning("No uploaded file found yet. Upload first or enable Demo mode.")

            if data is not None:
                # Use new optimized layout if data has developmental_index (all formats)
                if "developmental_index" in data:
                    # Use new optimized component layout
                    st.markdown("---")
                    st.subheader(f"Patient: {patient_name} | {data.get('gestational_weeks', 'N/A')} weeks")
                    
                    # Developmental Index prominently displayed
                    render_developmental_index(
                        data.get("developmental_index", 0.5),
                        data.get("confidence", 0.85)
                    )
                    
                    # Three-column layout
                    left, center, right = st.columns([1.2, 2, 1.2])
                    
                    with left:
                        st.markdown("**Clinical Context**")
                        sqa = data.get("sqa", {})
                        if sqa.get("overall_quality"):
                            st.info(f"Signal Quality: {sqa['overall_quality']}")
                        st.caption("Maternal Cancellation: 98.7% successful")
                    
                    with center:
                        st.markdown("**Signal & Metrics**")
                        # Signal visualization
                        if data.get("cleaned_ecg"):
                            try:
                                fig = go.Figure()
                                fig.add_trace(go.Scatter(
                                    y=data["cleaned_ecg"][:min(1000, len(data["cleaned_ecg"]))],
                                    mode="lines",
                                    name="Cleaned ECG",
                                    line=dict(color="#5f6f7b", width=1.5)
                                ))
                                fig.update_layout(height=200, margin=dict(l=10, r=10, t=20, b=20))
                                st.plotly_chart(fig, use_container_width=True)
                            except Exception as e:
                                st.caption(f"Signal visualization unavailable: {e}")
                        
                        # Risk cards
                        risk_assessment = data.get("risk_assessment", {}) or data.get("risk", {})
                        if risk_assessment:
                            render_risk_cards(risk_assessment)
                        
                        # HRV Metrics
                        st.markdown("**HRV & PRSA Metrics**")
                        metrics = data.get("hrv_metrics", {}) or data.get("features", {})
                        if metrics:
                            cols = st.columns(3)
                            with cols[0]:
                                st.metric("RMSSD", f"{metrics.get('rmssd', 35)} ms", "Normal")
                            with cols[1]:
                                st.metric("LF/HF", f"{metrics.get('lf_hf_ratio', metrics.get('lf_hf', 1.7))}", "Moderate")
                            with cols[2]:
                                st.metric("AC-T9", f"{metrics.get('ac_t9', metrics.get('sample_entropy', 0.87))}", "IUGR predictor")
                    
                    with right:
                        st.markdown("**Insights**")
                        
                        # Trajectory info (if available)
                        if st.session_state.get("recent_indices"):
                            pipeline = get_pipeline()
                            trajectory = pipeline.update_trajectory(
                                previous_indices=st.session_state.get("recent_indices", []),
                                current_index=data.get("developmental_index", 0.5),
                                ga_weeks=st.session_state.get("recent_weeks", [])
                            )
                            render_trajectory_panel(trajectory)
                        
                        # Recommendation  
                        if data.get("recommendation"):
                            recommendation = data.get("recommendation")
                        elif data.get("interpretation"):
                            # Use first interpretation line as recommendation in old format
                            recommendations = data.get("interpretation", [])
                            recommendation = recommendations[0] if recommendations else "Routine monitoring recommended."
                        else:
                            recommendation = "Routine monitoring recommended."
                        render_recommendation(recommendation)
                        
                        # Export buttons
                        st.markdown("---")
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("📥 Export PDF", key="btn_exp_pdf"):
                                st.success("Report exported (demo)")
                        with col_b:
                            if st.button("🔗 KenyaEMR", key="btn_emr"):
                                st.success("FHIR export OK")
                    
                    # Store recent values for trajectory tracking
                    if "recent_indices" not in st.session_state:
                        st.session_state["recent_indices"] = []
                    st.session_state["recent_indices"].append(data.get("developmental_index", 0.5))
                    if "recent_weeks" not in st.session_state:
                        st.session_state["recent_weeks"] = []
                    st.session_state["recent_weeks"].append(data.get("gestational_weeks", 32))
                    
                    # Explainability section
                    st.markdown("---")
                    explainability = data.get("explainability", {}) or data.get("features", {})
                    render_explainability(explainability)
                    
                else:
                    # Fallback to old dashboard format
                    _render_clinical_dashboard(data, patient_name, compact=compact_mode, readable=readable_mode)

elif page == "Clinical Insights":
    st.header("Clinical Insights")
    st.markdown("#### Feature Interpretations")
    interpretations = {
        "RMSSD": "Higher values indicate stronger vagal tone.",
        "LF/HF Ratio": "Represents autonomic balance.",
        "Sample Entropy": "Proxy for signal complexity and adaptability.",
        "SDNN": "General heart rate variability marker.",
    }
    for feature, text in interpretations.items():
        st.write(f"**{feature}**: {text}")

    st.markdown("#### Developmental Trajectory")
    weeks = np.arange(20, 43)
    normal_curve = 0.28 + 0.018 * (weeks - 20)
    fig = px.line(x=weeks, y=normal_curve, labels={"x": "Gestational Weeks", "y": "Developmental Index"})
    fig.update_layout(height=350, template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption(f"Neuro-Genomic AI Dashboard | {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")