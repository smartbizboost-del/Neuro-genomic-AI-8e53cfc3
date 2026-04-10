# ECG Preprocessing — bandpass filtering, baseline removal, normalisation, notch filter

import numpy as np
from scipy import signal


class ECGPreprocessor:

    def __init__(self, sampling_rate=500, lowcut=0.5, highcut=40, filter_order=4):
        self.fs = sampling_rate
        self.lowcut = lowcut
        self.highcut = highcut
        self.order = filter_order

        # Design Butterworth bandpass filter coefficients
        nyquist = self.fs / 2
        self.b, self.a = signal.butter(
            self.order,
            [lowcut / nyquist, highcut / nyquist],
            btype='band'
        )

    # Zero-phase bandpass filter (1D or multi-channel)
    def filter_signal(self, ecg_signal):
        if len(ecg_signal.shape) == 1:
            return signal.filtfilt(self.b, self.a, ecg_signal)
        filtered = np.zeros_like(ecg_signal)
        for i in range(ecg_signal.shape[1]):
            filtered[:, i] = signal.filtfilt(self.b, self.a, ecg_signal[:, i])
        return filtered

    # Subtract median-filtered baseline to remove wander
    def remove_baseline_wander(self, ecg_signal, window_size=None):
        if window_size is None:
            window_size = max(3, int(self.fs / 50) | 1)  # ensure odd
        baseline = signal.medfilt(ecg_signal, kernel_size=window_size)
        return ecg_signal - baseline

    # Z-score or min-max normalisation
    def normalize_signal(self, ecg_signal, method='zscore'):
        if method == 'zscore':
            mean = np.mean(ecg_signal, axis=0)
            std = np.std(ecg_signal, axis=0)
            return (ecg_signal - mean) / (std + 1e-8)
        elif method == 'minmax':
            mn = np.min(ecg_signal, axis=0)
            mx = np.max(ecg_signal, axis=0)
            return (ecg_signal - mn) / (mx - mn + 1e-8)
        else:
            raise ValueError("Method must be 'zscore' or 'minmax'")

    # Notch filter to remove 50/60 Hz powerline interference
    def remove_powerline_noise(self, ecg_signal, notch_freq=60):
        Q = 30  # quality factor
        w0 = notch_freq / (self.fs / 2)
        b, a = signal.iirnotch(w0, Q)
        if len(ecg_signal.shape) == 1:
            return signal.filtfilt(b, a, ecg_signal)
        filtered = np.zeros_like(ecg_signal)
        for i in range(ecg_signal.shape[1]):
            filtered[:, i] = signal.filtfilt(b, a, ecg_signal[:, i])
        return filtered

    # Compare raw vs filtered power to quantify noise reduction
    def get_noise_statistics(self, raw_signal, filtered_signal):
        raw_power = np.mean(raw_signal ** 2)
        filtered_power = np.mean(filtered_signal ** 2)
        noise_power = raw_power - filtered_power
        return {
            'raw_power': raw_power,
            'filtered_power': filtered_power,
            'noise_power': noise_power,
            'snr_improvement_db': 10 * np.log10(raw_power / (filtered_power + 1e-10))
        }
