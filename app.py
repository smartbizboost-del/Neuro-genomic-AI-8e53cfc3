import streamlit as st
import requests

st.set_page_config(layout="wide")

st.title("Neuro-Genomic AI Dashboard")

# Health Check
health = requests.get("http://localhost:8000/health").json()

st.subheader("System Health")
st.write(f"CPU: {health['cpu']}%")
st.write(f"Memory: {health['memory']}%")

# HRV Data
data = requests.get("http://localhost:8000/hrv").json()

st.subheader("Fetal HRV Metrics")
col1, col2, col3 = st.columns(3)

col1.metric("RMSSD", data["rmssd"])
col2.metric("LF/HF", data["lf_hf"])
col3.metric("Entropy", data["entropy"])

st.subheader("Clinical Interpretation")
st.warning(f"Risk Level: {data['risk']}")
