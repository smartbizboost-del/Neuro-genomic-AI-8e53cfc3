"""
Sidebar component for the Neuro-Genomic AI UI
"""

import streamlit as st


def render_sidebar():
    """Render the app sidebar"""
    st.sidebar.header("🧬 Neuro-Genomic AI")
    st.sidebar.markdown("---")

    # Navigation
    page = st.sidebar.radio(
        "Navigation",
        ["Upload & Analyze", "Results Viewer", "Clinical Insights", "Settings"]
    )

    # System status
    st.sidebar.markdown("---")
    st.sidebar.subheader("System Status")
    st.sidebar.success("API: Connected")
    st.sidebar.success("Database: Connected")
    st.sidebar.success("Worker: Active")

    return page
