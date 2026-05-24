"""Feature extraction converted from notebook 03_feature_extraction.ipynb.
Contains simple HRV and spectral features used by the rest of the system.
"""
import numpy as np
from scipy.signal import welch


def sample_entropy(signal, m=2, r=None):
    # Very small, fast approximation (not production-grade)
    x = np.array(signal)
    n = len(x)
    if n < 10:
        return float('nan')
    if r is None:
        r = 0.2 * np.std(x)
    def _phi(m):
        count = 0
        for i in range(n - m + 1):
            for j in range(i+1, n - m + 1):
                if np.max(np.abs(x[i:i+m] - x[j:j+m])) <= r:
                    count += 1
        return count
    try:
        return -np.log(_phi(m+1) / _phi(m))
    except Exception:
        return float('nan')


def lf_hf_ratio(rr_intervals_ms, fs=4.0):
    # Convert RR intervals to evenly-sampled signal using simple interpolation
    if len(rr_intervals_ms) < 4:
        return float('nan')
    t = np.cumsum(np.concatenate([[0], rr_intervals_ms]))/1000.0
    # create evenly sampled at fs Hz
    t_uniform = np.arange(0, t[-1], 1.0/fs)
    try:
        rr_uniform = np.interp(t_uniform, t[:-1], rr_intervals_ms)
    except Exception:
        return float('nan')
    f, pxx = welch(rr_uniform, fs=fs, nperseg=min(256, len(rr_uniform)))
    lf_band = (0.04, 0.15)
    hf_band = (0.15, 0.4)
    lf = np.trapz(pxx[(f >= lf_band[0]) & (f < lf_band[1])], f[(f >= lf_band[0]) & (f < lf_band[1])])
    hf = np.trapz(pxx[(f >= hf_band[0]) & (f < hf_band[1])], f[(f >= hf_band[0]) & (f < hf_band[1])])
    if hf == 0:
        return float('inf')
    return float(lf / hf)


def run(rr_intervals_ms):
    return {
        'sample_entropy': float(sample_entropy(rr_intervals_ms)),
        'lf_hf_ratio': float(lf_hf_ratio(rr_intervals_ms)),
    }
