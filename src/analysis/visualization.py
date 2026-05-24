"""Visualization helpers (06_visualize_expected_outcomes.ipynb)
Provide small functions that return data payloads suitable for plotting in frontend.
"""
import numpy as np


def expected_development_curve(weeks=24, up_to=40):
    ws = list(range(weeks, up_to+1))
    values = [0.6 + 0.005*(w-weeks) + 0.02*np.sin(w/3.2) for w in ws]
    return {'weeks': ws, 'development_index': values}


def run():
    return expected_development_curve()
