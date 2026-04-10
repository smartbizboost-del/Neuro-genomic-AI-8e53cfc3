# Feature Extraction — R-peak detection and HRV metrics from ECG signals

import numpy as np
from scipy.signal import find_peaks


class HRVExtractor:

    def __init__(self, sampling_rate=500):
        self.fs = sampling_rate

    # Adaptive-threshold R-peak detection (min distance 0.4 s → 200 bpm cap)
    def detect_r_peaks(self, ecg_signal, threshold_multiplier=2.0):
        signal_abs = np.abs(ecg_signal)
        threshold = np.mean(signal_abs) + threshold_multiplier * np.std(signal_abs)
        min_distance = int(self.fs * 0.4)
        peaks, _ = find_peaks(signal_abs, height=threshold, distance=min_distance)
        return peaks

    # Time-domain HRV features from a single ECG channel
    def extract_features(self, ecg_signal):
        peaks = self.detect_r_peaks(ecg_signal)
        if len(peaks) < 2:
            return self._get_empty_features()

        # RR intervals in milliseconds
        rr_intervals = np.diff(peaks) / self.fs * 1000

        # Heart rate stats
        heart_rate = 60 / (np.mean(rr_intervals) / 1000)
        hr_std = np.std(60 / (rr_intervals / 1000))

        # RR interval stats
        rr_mean = np.mean(rr_intervals)
        rr_std = np.std(rr_intervals)

        # RMSSD — root mean square of successive RR differences
        rmssd = np.sqrt(np.mean(np.diff(rr_intervals) ** 2))

        # pNN50 — % of successive RR diffs > 50 ms
        pnn50 = 100 * np.sum(np.abs(np.diff(rr_intervals)) > 50) / len(rr_intervals)

        return {
            'num_beats': len(peaks),
            'heart_rate_mean': heart_rate,
            'heart_rate_std': hr_std,
            'rr_interval_mean': rr_mean,
            'rr_interval_std': rr_std,
            'rmssd': rmssd,
            'pnn50': pnn50,
            'r_peaks': peaks,
            'rr_intervals': rr_intervals
        }

    # Extract features for multiple named signals at once
    def extract_batch_features(self, signals_dict):
        return {name: self.extract_features(sig) for name, sig in signals_dict.items()}

    # NaN placeholder when fewer than 2 beats detected
    @staticmethod
    def _get_empty_features():
        return {
            'num_beats': 0,
            'heart_rate_mean': np.nan,
            'heart_rate_std': np.nan,
            'rr_interval_mean': np.nan,
            'rr_interval_std': np.nan,
            'rmssd': np.nan,
            'pnn50': np.nan,
            'r_peaks': np.array([]),
            'rr_intervals': np.array([])
        }
