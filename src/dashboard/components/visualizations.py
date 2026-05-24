"""
Visualization components for dashboard
"""

import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import pandas as pd


def plot_risk_assessment(risk_data: dict):
    """Plot risk assessment as a bar chart"""
    df = pd.DataFrame.from_dict(
        risk_data,
        orient='index',
        columns=['Probability'])
    fig = px.bar(
        df,
        title="Risk Assessment",
        labels={
            'index': 'Category',
            'value': 'Probability'})
    return fig


def plot_developmental_gauge(index: float):
    """Plot developmental index as a gauge"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=index * 100,
        title={'text': "Developmental Health"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 40], 'color': "red"},
                {'range': [40, 70], 'color': "yellow"},
                {'range': [70, 100], 'color': "green"}
            ]
        }
    ))
    return fig


def plot_feature_comparison(features: dict):
    """Plot HRV features comparison"""
    df = pd.DataFrame.from_dict(features, orient='index', columns=['Value'])
    fig = px.bar(df, title="HRV Features", orientation='h')
    return fig
