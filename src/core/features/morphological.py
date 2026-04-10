import numpy as np
from scipy.signal import find_peaks


def detect_r_peaks(ecg_signal: np.ndarray, fs: int = 250, distance_sec: float = 0.25) -> np.ndarray:
    """Detect R peaks in a fetal ECG signal."""
    threshold = np.mean(np.abs(ecg_signal)) + 1.5 * np.std(np.abs(ecg_signal))
    distance = int(fs * distance_sec)
    peaks, _ = find_peaks(np.abs(ecg_signal), height=threshold, distance=distance)
    return peaks


def calculate_t_qrs_ratio(ecg_signal: np.ndarray, r_peaks: np.ndarray, fs: int = 250):
    """
    Calculate T/QRS ratio for hypoxia detection
    T wave amplitude / QRS complex amplitude
    """
    t_qrs_ratios = []
    for r_peak in r_peaks:
        qrs_start = max(0, r_peak - int(0.05 * fs))
        qrs_end = min(len(ecg_signal), r_peak + int(0.10 * fs))
        qrs_segment = ecg_signal[qrs_start:qrs_end]
        if qrs_segment.size == 0:
            continue
        qrs_amp = np.max(qrs_segment) - np.min(qrs_segment)

        t_start = r_peak + int(0.15 * fs)
        t_end = min(len(ecg_signal), r_peak + int(0.30 * fs))
        t_segment = ecg_signal[t_start:t_end]
        if t_segment.size == 0:
            continue

        t_amp = np.max(t_segment) - np.min(t_segment)

        if qrs_amp > 0:
            t_qrs_ratios.append(float(t_amp / qrs_amp))

    mean_ratio = float(np.mean(t_qrs_ratios)) if t_qrs_ratios else None
    return {
        't_qrs_ratio': mean_ratio,
        'hypoxia_risk': 'high' if mean_ratio is not None and mean_ratio > 0.25 else 'low' if mean_ratio is not None else 'unknown',
        'num_beats': int(len(r_peaks))
    }
