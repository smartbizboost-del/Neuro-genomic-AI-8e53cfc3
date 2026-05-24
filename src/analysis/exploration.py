"""Exploration helpers (exploration.ipynb)
Small helpers used during development and debugging.
"""

import numpy as np


def random_signal(fs=500, seconds=10):
    t = np.linspace(0, seconds, fs*seconds, endpoint=False)
    sig = 0.5*np.sin(2*np.pi*1.2*t) + 0.2*np.random.randn(len(t))
    return t, sig


def run():
    t, sig = random_signal()
    return {'t_len': len(t), 'sig_mean': float(sig.mean())}
