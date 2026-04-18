"""
Report generation components
"""

import streamlit as st
from typing import Dict, Any


def generate_report(data: Dict[str, Any]):
    """Generate a clinical report"""
    st.header("Clinical Report")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Patient Information")
        st.write(f"File ID: {data.get('file_id', 'N/A')}")
        st.write(f"Gestational Weeks: {data.get('gestational_weeks', 'N/A')}")
        st.write(f"Analysis Date: {data.get('created_at', 'N/A')}")

    with col2:
        st.subheader("Key Findings")
        risk = data.get('risk', {})
        predicted = risk.get('predicted_class', 'unknown')
        st.write(f"Risk Classification: {predicted.upper()}")
        st.write(
            f"Developmental Index: {
                data.get(
                    'developmental_index',
                    0):.2f}")

    st.subheader("Clinical Interpretation")
    for interp in data.get('interpretation', []):
        st.write(f"• {interp}")

    if st.button("Export PDF"):
        st.info("PDF export functionality coming soon!")
