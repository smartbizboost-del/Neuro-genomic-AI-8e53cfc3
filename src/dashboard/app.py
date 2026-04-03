"""
Streamlit dashboard for Neuro-Genomic AI
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any
import os

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Neuro-Genomic AI Dashboard",
    page_icon="🧬",
    layout="wide"
)

st.title("🧬 Neuro-Genomic AI Dashboard")
st.markdown("*Ethical AI for Fetal Development Monitoring*")

# Sidebar
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Upload & Analyze", "Results Viewer", "Clinical Insights"])

if page == "Upload & Analyze":
    st.header("Upload Fetal ECG File")
    
    uploaded_file = st.file_uploader("Choose a fetal ECG file", type=['csv', 'txt', 'edf'])
    gestational_weeks = st.number_input("Gestational Weeks", min_value=20, max_value=42, value=32)
    patient_id = st.text_input("Patient ID (optional)")
    
    if st.button("Analyze", type="primary") and uploaded_file is not None:
        with st.spinner("Uploading and processing..."):
            # Upload file
            files = {"file": uploaded_file}
            data = {"gestational_weeks": gestational_weeks, "patient_id": patient_id}
            
            try:
                response = requests.post(f"{API_URL}/api/v1/upload", files=files, data=data)
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"File uploaded successfully! File ID: {result['file_id']}")
                    st.info("Processing in background. Check Results Viewer for analysis.")
                else:
                    st.error(f"Upload failed: {response.text}")
            except Exception as e:
                st.error(f"Error: {e}")

elif page == "Results Viewer":
    st.header("Analysis Results")
    
    file_id = st.text_input("Enter File ID")
    
    if st.button("Get Results") and file_id:
        with st.spinner("Fetching results..."):
            try:
                response = requests.get(f"{API_URL}/api/v1/analysis/{file_id}")
                if response.status_code == 200:
                    data = response.json()
                    
                    # Display results
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("HRV Features")
                        features_df = pd.DataFrame.from_dict(data['features'], orient='index', columns=['Value'])
                        st.dataframe(features_df)
                        
                        st.subheader("Risk Assessment")
                        # Filter out non-numeric keys for the chart
                        risk_probs = {k: v for k, v in data['risk'].items() if k in ['normal', 'suspect', 'pathological']}
                        risk_df = pd.DataFrame.from_dict(risk_probs, orient='index', columns=['Probability'])
                        st.bar_chart(risk_df)
                        
                        st.caption(f"Model used: **{data['risk'].get('model_used', 'Supervised Classifier')}**")
                        
                        st.subheader("Unsupervised Analysis")
                        anomaly_score = data['risk'].get('anomaly_score', 0)
                        cluster = data['risk'].get('unsupervised_cluster', 'N/A')
                        st.metric("Anomaly Score (Neg Log-Likelihood)", f"{anomaly_score:.2f}",
                                  delta="Anomalous" if anomaly_score > 15 else "Normal",
                                  delta_color="inverse")
                        st.write(f"Assigned Cluster: **{cluster}**")
                    
                    with col2:
                        st.subheader("Clinical Interpretation")
                        for interp in data['interpretation']:
                            st.write(f"• {interp}")
                        
                        st.subheader("Developmental Index")
                        st.metric("Index", f"{data['developmental_index']:.2f}")
                        
                        # Risk gauge
                        fig = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=data['developmental_index'] * 100,
                            title={'text': "Developmental Health"},
                            gauge={'axis': {'range': [0, 100]},
                                   'bar': {'color': "darkblue"},
                                   'steps': [
                                       {'range': [0, 40], 'color': "red"},
                                       {'range': [40, 70], 'color': "yellow"},
                                       {'range': [70, 100], 'color': "green"}]}))
                        st.plotly_chart(fig)
                        
                else:
                    st.error(f"Failed to get results: {response.text}")
            except Exception as e:
                st.error(f"Error: {e}")

elif page == "Clinical Insights":
    st.header("Clinical Insights & Research")
    
    st.subheader("Feature Interpretations")
    interpretations = {
        "RMSSD": "Vagal tone - higher values indicate mature parasympathetic system",
        "LF/HF Ratio": "Autonomic balance - lower values suggest healthy rest state",
        "Sample Entropy": "Neural complexity - peaks around 32 weeks optimal development",
        "SDNN": "Overall HRV - reflects autonomic nervous system maturity"
    }
    
    for feature, desc in interpretations.items():
        st.write(f"**{feature}**: {desc}")
    
    st.subheader("Developmental Trajectory")
    # Placeholder chart
    weeks = list(range(20, 43))
    normal_trajectory = [0.3 + 0.02 * (w - 20) for w in weeks]
    fig = px.line(x=weeks, y=normal_trajectory, 
                  title="Normal Developmental Trajectory",
                  labels={'x': 'Gestational Weeks', 'y': 'Developmental Index'})
    st.plotly_chart(fig)

# Footer
st.markdown("---")
st.markdown("**Neuro-Genomic AI** - Ethical AI for fetal development monitoring")
st.markdown("Built with ❤️ by Collins Omondi")