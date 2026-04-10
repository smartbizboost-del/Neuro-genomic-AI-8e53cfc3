from __future__ import annotations

import numpy as np
from scipy import signal


class ECGPreprocessor:
    def __init__(self, sampling_rate: int = 500, lowcut: float = 0.5, highcut: float = 45.0, order: int = 4):
        self.fs = sampling_rate
        nyquist = self.fs / 2.0
        self.band_b, self.band_a = signal.butter(order, [lowcut / nyquist, highcut / nyquist], btype="band")

    def bandpass(self, x: np.ndarray) -> np.ndarray:
        if x.ndim == 1:
            return signal.filtfilt(self.band_b, self.band_a, x)
        out = np.zeros_like(x)
        for i in range(x.shape[1]):
            out[:, i] = signal.filtfilt(self.band_b, self.band_a, x[:, i])
        return out

    def notch(self, x: np.ndarray, freq: float = 50.0, q: float = 30.0) -> np.ndarray:
        w0 = freq / (self.fs / 2.0)
        b, a = signal.iirnotch(w0=w0, Q=q)
        if x.ndim == 1:
            return signal.filtfilt(b, a, x)
        out = np.zeros_like(x)
        for i in range(x.shape[1]):
            out[:, i] = signal.filtfilt(b, a, x[:, i])
        return out

    def remove_baseline(self, x: np.ndarray, window_samples: int | None = None) -> np.ndarray:
        if window_samples is None:
            window_samples = max(5, int(self.fs * 0.2) | 1)
        if x.ndim == 1:
            base = signal.medfilt(x, kernel_size=window_samples)
            return x - base
        out = np.zeros_like(x)
        for i in range(x.shape[1]):
            base = signal.medfilt(x[:, i], kernel_size=window_samples)
            out[:, i] = x[:, i] - base
        return out

    @staticmethod
    def zscore(x: np.ndarray) -> np.ndarray:
        mean = np.mean(x, axis=0)
        std = np.std(x, axis=0) + 1e-8
        return (x - mean) / std

    def transform(self, x: np.ndarray) -> np.ndarray:
        y = self.bandpass(x)
        y = self.notch(y)
        y = self.remove_baseline(y)
        return self.zscore(y)
