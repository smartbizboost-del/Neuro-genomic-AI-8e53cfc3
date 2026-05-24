"""Analysis helpers converted from notebooks: signal preprocessing and ICA separation.
This module provides functions to load signals (DB or synthetic), filter, run ICA,
and extract HRV features. Intended to be used by the CLI and FastAPI endpoints.
"""
from pathlib import Path
import sqlite3
import numpy as np
import pandas as pd
import scipy.signal as signal
from scipy.signal import find_peaks
from sklearn.decomposition import FastICA

np.random.seed(42)


def load_ecg_from_db(db_path: str | Path, fs_default: int = 500, duration_default: int = 10):
    db_path = Path(db_path)
    fs = fs_default
    duration = duration_default
    loaded_from = "synthetic"

    if db_path.exists():
        try:
            with sqlite3.connect(db_path) as conn:
                tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)["name"].tolist()
                if "raw_ecg" in tables:
                    raw_df = pd.read_sql_query('SELECT * FROM raw_ecg', conn)
                    if {"time_s", "ch1", "ch2"}.issubset(raw_df.columns):
                        t = raw_df['time_s'].values
                        ecg_signal = raw_df[['ch1', 'ch2']].to_numpy()
                        fs = int(raw_df['fs'].iloc[0]) if 'fs' in raw_df.columns else fs
                        duration = float(t[-1] - t[0]) if len(t) > 1 else duration
                        loaded_from = 'database: raw_ecg'
                        return t, ecg_signal, fs, duration, loaded_from
                elif 'separated_components' in tables:
                    sep_df = pd.read_sql_query('SELECT * FROM separated_components', conn)
                    if {'time_s', 'maternal_ecg', 'fetal_ecg'}.issubset(sep_df.columns):
                        t = sep_df['time_s'].values
                        maternal_ecg = sep_df['maternal_ecg'].values
                        fetal_ecg = sep_df['fetal_ecg'].values
                        mixed_ch1 = 0.7 * maternal_ecg + 0.5 * fetal_ecg + 0.4 * np.random.randn(len(t))
                        mixed_ch2 = 0.6 * maternal_ecg + 0.6 * fetal_ecg + 0.3 * np.random.randn(len(t))
                        ecg_signal = np.column_stack([mixed_ch1, mixed_ch2])
                        duration = float(t[-1] - t[0]) if len(t) > 1 else duration
                        loaded_from = 'database: separated_components (remixed)'
                        return t, ecg_signal, fs, duration, loaded_from
        except Exception:
            pass

    # Synthetic fallback
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
    maternal_ecg = 5 * np.sin(2 * np.pi * 1.2 * t) + 0.3 * np.random.randn(len(t))
    fetal_ecg = 2.5 * np.sin(2 * np.pi * 2.4 * t + np.pi / 4) + 0.2 * np.random.randn(len(t))
    mixed_ch1 = 0.7 * maternal_ecg + 0.5 * fetal_ecg + 0.4 * np.random.randn(len(t))
    mixed_ch2 = 0.6 * maternal_ecg + 0.6 * fetal_ecg + 0.3 * np.random.randn(len(t))
    ecg_signal = np.column_stack([mixed_ch1, mixed_ch2])
    return t, ecg_signal, fs, duration, loaded_from


def butter_bandpass_filter(ecg_signal: np.ndarray, fs: int, lowcut=0.5, highcut=40.0, order=4):
    nyq = fs / 2
    if nyq <= 0:
        raise ValueError("Sampling frequency must be positive")

    low = lowcut / nyq
    high = highcut / nyq
    low = max(0.001, min(low, 0.99))
    high = max(0.01, min(high, 0.99))

    if low >= high:
        low = max(0.001, min(low, high * 0.5))

    b, a = signal.butter(order, [low, high], btype='band')
    filtered_ch1 = signal.filtfilt(b, a, ecg_signal[:, 0])
    filtered_ch2 = signal.filtfilt(b, a, ecg_signal[:, 1])
    filtered_signal = np.column_stack([filtered_ch1, filtered_ch2])
    return filtered_signal


def run_ica(filtered_signal: np.ndarray, n_components: int = 2, random_state: int = 42):
    ica = FastICA(n_components=n_components, max_iter=500, random_state=random_state, whiten='unit-variance')
    independent_components = ica.fit_transform(filtered_signal)
    mixing_matrix = ica.mixing_
    return independent_components, mixing_matrix


def extract_heart_rate_features(ecg_component: np.ndarray, sampling_rate: int, component_name='Component') -> tuple[dict | None, np.ndarray]:
    signal_abs = np.abs(ecg_component)
    threshold = np.mean(signal_abs) + 2 * np.std(signal_abs)
    peaks, _ = find_peaks(signal_abs, height=threshold, distance=sampling_rate * 0.4)
    if len(peaks) < 2:
        return None, np.array([])
    rr_intervals = np.diff(peaks) / sampling_rate * 1000
    heart_rate = 60 / (np.mean(rr_intervals) / 1000)
    hrv_features = {
        'component': component_name,
        'num_beats': len(peaks),
        'heart_rate_mean': heart_rate,
        'heart_rate_std': np.std(60 / (rr_intervals / 1000)),
        'rr_interval_mean': np.mean(rr_intervals),
        'rr_interval_std': np.std(rr_intervals),
        'rmssd': np.sqrt(np.mean(np.diff(rr_intervals) ** 2)),
        'pnn50': 100 * np.sum(np.abs(np.diff(rr_intervals)) > 50) / len(rr_intervals),
    }
    return hrv_features, peaks


if __name__ == '__main__':
    # Small sanity check when run directly
    t, ecg_signal, fs, duration, src = load_ecg_from_db(Path('../data/processed/neuro_genomic.db'))
    filtered = butter_bandpass_filter(ecg_signal, fs)
    ics, mixing = run_ica(filtered)
    f1, p1 = extract_heart_rate_features(ics[:, 0], fs, 'IC1')
    f2, p2 = extract_heart_rate_features(ics[:, 1], fs, 'IC2')
    print('Loaded from:', src)
    print('ECG shape:', ecg_signal.shape)
    print('HRV IC1:', f1)
    print('HRV IC2:', f2)
