"""ICA separation helpers (converted from notebook 02_signal_separation.ipynb).
Provides a simple wrapper around `run_ica` and utilities to reconstruct mixed signals.
"""
from typing import Tuple
import numpy as np
from .preprocessing import run_ica


def separate_and_reconstruct(mixed_signal: np.ndarray) -> dict:
    ics, mixing = run_ica(mixed_signal)
    reconstructed = np.dot(ics, mixing.T)
    return {
        "ics": ics,
        "mixing": mixing,
        "reconstructed": reconstructed,
    }


def run(mixed_signal: np.ndarray) -> dict:
    return separate_and_reconstruct(mixed_signal)
