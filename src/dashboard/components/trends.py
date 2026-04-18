import plotly.express as px
import pandas as pd


def plot_developmental_trend(historical_data):
    """Render gestational trajectory trend chart."""
    df = pd.DataFrame(historical_data)
    fig = px.line(
        df,
        x='gestational_weeks',
        y='developmental_index',
        title='Developmental Trajectory',
        labels={
            'gestational_weeks': 'Gestational Weeks',
            'developmental_index': 'Developmental Index'})
    return fig


def plot_cohort_benchmark(cohort_data, patient_index):
    """Plot patient developmental index against a cohort."""
    df = pd.DataFrame(cohort_data)
    fig = px.histogram(
        df,
        x='developmental_index',
        nbins=10,
        title='Cohort Benchmark',
        labels={
            'developmental_index': 'Developmental Index'})
    fig.add_vline(
        x=patient_index,
        line_dash='dash',
        line_color='red',
        annotation_text='Patient')
    return fig
