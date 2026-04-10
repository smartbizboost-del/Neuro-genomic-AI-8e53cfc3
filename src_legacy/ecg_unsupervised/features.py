from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.signal import find_peaks


class WindowedFeatureExtractor:
    def __init__(self, sampling_rate: int = 500, window_sec: int = 10):
        self.fs = sampling_rate
        self.window_samples = sampling_rate * window_sec

    def _detect_peaks(self, x: np.ndarray, distance_sec: float = 0.30) -> np.ndarray:
        threshold = np.mean(np.abs(x)) + 1.5 * np.std(np.abs(x))
        distance = int(self.fs * distance_sec)
        peaks, _ = find_peaks(np.abs(x), height=threshold, distance=distance)
        return peaks

    def _hrv(self, x: np.ndarray) -> dict[str, float]:
        peaks = self._detect_peaks(x)
        if len(peaks) < 2:
            return {
                "num_beats": 0.0,
                "hr_mean": np.nan,
                "rr_mean": np.nan,
                "rr_std": np.nan,
                "rmssd": np.nan,
                "pnn50": np.nan,
            }
        rr_ms = np.diff(peaks) / self.fs * 1000.0
        hr = 60.0 / (rr_ms / 1000.0)
        rr_diff = np.diff(rr_ms)
        return {
            "num_beats": float(len(peaks)),
            "hr_mean": float(np.mean(hr)),
            "rr_mean": float(np.mean(rr_ms)),
            "rr_std": float(np.std(rr_ms)),
            "rmssd": float(np.sqrt(np.mean(rr_diff ** 2))) if len(rr_diff) else 0.0,
            "pnn50": float(100.0 * np.mean(np.abs(rr_diff) > 50.0)) if len(rr_diff) else 0.0,
        }

    @staticmethod
    def _spectral_power(x: np.ndarray, fs: int, lo: float, hi: float) -> float:
        freqs = np.fft.rfftfreq(len(x), d=1.0 / fs)
        power = np.abs(np.fft.rfft(x)) ** 2
        mask = (freqs >= lo) & (freqs <= hi)
        return float(np.sum(power[mask]))

    def extract(self, maternal: np.ndarray, fetal: np.ndarray) -> pd.DataFrame:
        rows: list[dict[str, float]] = []
        win = self.window_samples
        for start in range(0, len(maternal) - win + 1, win):
            end = start + win
            m = maternal[start:end]
            f = fetal[start:end]
            m_hrv = self._hrv(m)
            f_hrv = self._hrv(f)
            rows.append(
                {
                    "window_start": float(start),
                    "window_end": float(end),
                    "mat_hr_mean": m_hrv["hr_mean"],
                    "fet_hr_mean": f_hrv["hr_mean"],
                    "mat_rmssd": m_hrv["rmssd"],
                    "fet_rmssd": f_hrv["rmssd"],
                    "mat_pnn50": m_hrv["pnn50"],
                    "fet_pnn50": f_hrv["pnn50"],
                    "mat_rr_std": m_hrv["rr_std"],
                    "fet_rr_std": f_hrv["rr_std"],
                    "mat_low_freq_power": self._spectral_power(m, self.fs, 0.04, 0.15),
                    "mat_high_freq_power": self._spectral_power(m, self.fs, 0.15, 0.40),
                    "fet_low_freq_power": self._spectral_power(f, self.fs, 0.04, 0.15),
                    "fet_high_freq_power": self._spectral_power(f, self.fs, 0.15, 0.40),
                    "mat_signal_std": float(np.std(m)),
                    "fet_signal_std": float(np.std(f)),
                }
            )
        df = pd.DataFrame(rows).dropna().reset_index(drop=True)
        return df
