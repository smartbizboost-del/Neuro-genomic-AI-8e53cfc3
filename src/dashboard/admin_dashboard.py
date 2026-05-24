import streamlit as st
import pandas as pd
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")


def render_admin_dashboard():
    st.header("Admin Dashboard")
    st.markdown("Manage users, review metrics, and track audit activity.")

    try:
        response = requests.get(f"{API_URL}/api/v1/admin/metrics")
        if response.status_code == 200:
            metrics = response.json()
            st.subheader("System Summary")
            st.metric("Total Users", metrics["users"]["total"])
            st.metric("Active Users", metrics["users"]["active"])
            st.metric("Daily Analyses", metrics["analyses"]["today"])

            st.subheader("API Status")
            st.write(metrics["api"])
            st.subheader("System Health")
            st.write(metrics["system"])

            st.subheader("Role Distribution")
            st.write(
                pd.DataFrame.from_dict(
                    metrics["users"]["by_role"],
                    orient='index',
                    columns=['Count']))
        else:
            st.warning("Unable to fetch admin metrics from API.")
    except Exception as exc:
        st.error(f"Admin dashboard error: {exc}")
