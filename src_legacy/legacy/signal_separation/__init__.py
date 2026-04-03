# Signal Separation — FastICA for maternal-fetal ECG decomposition

import numpy as np
from sklearn.decomposition import FastICA


class SignalSeparator:

    def __init__(self, n_components=2, random_state=42):
        self.n_components = n_components
        self.ica = FastICA(
            n_components=n_components,
            max_iter=500,
            random_state=random_state,
            whiten='unit-variance'
        )
        self.components_ = None
        self.mixing_matrix_ = None

    # Fit ICA and return separated independent components (n_samples, n_components)
    def fit_transform(self, mixed_signals):
        self.components_ = self.ica.fit_transform(mixed_signals)
        self.mixing_matrix_ = self.ica.mixing_
        return self.components_

    def get_sources(self):
        if self.components_ is None:
            raise ValueError("Model not fitted yet. Call fit_transform first.")
        return self.components_

    def get_mixing_matrix(self):
        if self.mixing_matrix_ is None:
            raise ValueError("Model not fitted yet. Call fit_transform first.")
        return self.mixing_matrix_

    def get_unmixing_matrix(self):
        if self.ica.components_ is None:
            raise ValueError("Model not fitted yet. Call fit_transform first.")
        return self.ica.components_

    # Reconstruct the mixed signal contribution of a single component
    def reconstruct_signal(self, component_index):
        single = np.zeros_like(self.components_)
        single[:, component_index] = self.components_[:, component_index]
        unmixing_inv = np.linalg.pinv(self.ica.components_)
        return single @ unmixing_inv.T

    # NMSE + correlation between original mixed and reconstructed signals
    def estimate_quality(self, original_mixed, reconstructed):
        nmse = np.mean((original_mixed - reconstructed) ** 2) / np.mean(original_mixed ** 2)
        corr = np.corrcoef(original_mixed.flatten(), reconstructed.flatten())[0, 1]
        return {
            'nmse': nmse,
            'correlation': corr,
            'reconstruction_error_percent': nmse * 100
        }


class ComponentAnalyzer:

    # Dominant frequency in 0.5–5 Hz range via FFT
    @staticmethod
    def estimate_component_frequency(component, sampling_rate):
        fft = np.abs(np.fft.fft(component))
        freqs = np.fft.fftfreq(len(component), 1 / sampling_rate)
        valid = (freqs > 0.5) & (freqs < 5)
        return freqs[valid][np.argmax(fft[valid])]

    # Label each component: Maternal (1–1.67 Hz) or Fetal (2–2.67 Hz)
    @staticmethod
    def classify_components(components, sampling_rate):
        classifications = {}
        frequencies = {}
        for i, comp in enumerate(components.T):
            freq = ComponentAnalyzer.estimate_component_frequency(comp, sampling_rate)
            frequencies[i] = freq
            if freq < 1.5:
                classifications[i] = 'Unknown (slow)'
            elif 1.5 <= freq < 2.0:
                classifications[i] = 'Maternal'
            elif 2.0 <= freq < 3.0:
                classifications[i] = 'Fetal'
            else:
                classifications[i] = 'Unknown (fast)'
        return {'classifications': classifications, 'frequencies': frequencies}
