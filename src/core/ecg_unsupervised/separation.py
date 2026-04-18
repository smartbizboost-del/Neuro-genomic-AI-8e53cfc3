from __future__ import annotations

import numpy as np
from sklearn.decomposition import FastICA


class FetalECGSeparator:
    def __init__(self, n_components: int = 2, random_state: int = 42):
        self.n_components = n_components
        self.ica = FastICA(
            n_components=n_components,
            whiten="unit-variance",
            random_state=random_state,
            max_iter=1000)
        self.components_: np.ndarray | None = None

    def fit_transform(self, mixed: np.ndarray) -> np.ndarray:
        self.components_ = self.ica.fit_transform(mixed)
        return self.components_

    def get_mixing_matrix(self) -> np.ndarray:
        return self.ica.mixing_

    def get_unmixing_matrix(self) -> np.ndarray:
        return np.linalg.pinv(self.ica.mixing_)

    @staticmethod
    def dominant_frequency_hz(signal: np.ndarray, fs: int) -> float:
        spectrum = np.abs(np.fft.rfft(signal))
        freqs = np.fft.rfftfreq(len(signal), d=1.0 / fs)
        valid = (freqs >= 0.5) & (freqs <= 4.0)
        if not np.any(valid):
            return 0.0
        return float(freqs[valid][np.argmax(spectrum[valid])])

    def infer_maternal_fetal_indices(self, fs: int) -> tuple[int, int]:
        if self.components_ is None:
            raise ValueError(
                "Call fit_transform before inferring maternal/fetal components.")

        freqs = {
            idx: self.dominant_frequency_hz(
                self.components_[
                    :, idx], fs) for idx in range(
                self.components_.shape[1])}
        maternal_idx = min(freqs, key=freqs.get)
        fetal_idx = max(freqs, key=freqs.get)
        return maternal_idx, fetal_idx

    def estimate_quality(self, original: np.ndarray,
                         reconstructed: np.ndarray) -> dict[str, float]:
        nmse = np.mean((original - reconstructed) ** 2) / np.var(original)
        corr = np.corrcoef(original.flatten(), reconstructed.flatten())[0, 1]
        return {"nmse": nmse, "correlation": corr}
