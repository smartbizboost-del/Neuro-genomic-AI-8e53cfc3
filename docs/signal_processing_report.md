# Signal Processing Report — Neuro-Genomic AI Pipeline

> **Document type:** Technical methodology report  
> **Version:** 1.0 | March 2026  
> **Scope:** Preprocessing, Source Separation, Feature Extraction

---

## 1. Introduction

This report documents the signal processing decisions made in the Neuro-Genomic AI research prototype. The pipeline processes mixed maternal-fetal ECG recordings to extract Heart Rate Variability (HRV) features that serve as proxies for fetal autonomic maturation. All implementation details reference the codebase at `src/`.

---

## 2. Signal Acquisition Assumptions

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Sampling rate (`fs`) | 500 Hz | Standard for fetal ECG research; satisfies Nyquist for signals up to 250 Hz |
| Signal duration | 10 seconds (minimum) | Provides ≥10 beats at 60 bpm; sufficient for time-domain HRV estimates |
| Input channels | ≥2 mixed abdominal leads | Required for ICA to resolve ≥2 independent sources |
| Amplitude units | Normalised (zero-mean, unit-variance) after scaling | Ensures ICA convergence |

---

## 3. Preprocessing (`src/preprocessing/__init__.py`)

### 3.1 Bandpass Filtering

**Filter design:** Butterworth bandpass, 4th order, zero-phase  
**Passband:** 0.5 – 40 Hz  
**Implementation:** `scipy.signal.butter` + `scipy.signal.filtfilt`

**Rationale:**
- Lower cut-off (0.5 Hz): Removes baseline wander caused by respiration and electrode drift without distorting the P-wave or ST segment.
- Upper cut-off (40 Hz): Eliminates high-frequency EMG artefacts from maternal muscle activity while preserving the QRS complex (dominant energy 5–30 Hz).
- Butterworth response: Maximally flat passband; no ripple that could introduce artefactual oscillations into RR intervals.
- Zero-phase (`filtfilt`): Eliminates filter-induced phase delay, critical for accurate R-peak latency estimation.

**Trade-offs:**
- 4th order introduces ≈−24 dB/octave roll-off; steeper filters would risk ringing near the QRS.
- Signal truncation artefact at edges is handled by `scipy`'s default padding strategy.

### 3.2 Normalisation

After filtering, each channel is z-scored (zero-mean, unit-variance) to ensure comparable amplitude scales across leads. This is a prerequisite for FastICA's whitening step.

---

## 4. Signal Separation (`src/signal_separation/__init__.py`)

### 4.1 FastICA

**Algorithm:** Fast Independent Component Analysis (Hyvärinen & Oja, 2000)  
**Implementation:** `sklearn.decomposition.FastICA`

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `n_components` | 2 | Target two sources: maternal ECG and fetal ECG |
| `whiten` | `'unit-variance'` | Pre-whitens data; decorrelates and equalises variances before rotation |
| `max_iter` | 500 | Allows convergence for difficult mixed signals |
| `random_state` | 42 | Reproducibility |
| Nonlinearity (`fun`) | `'logcosh'` (default) | Robust to outliers; good for super-Gaussian ECG distributions |

**Mathematical basis:**  
ICA models the observed M-channel signal **x** as a linear mixture of N independent sources **s**:

$$\mathbf{x} = \mathbf{A}\mathbf{s}$$

FastICA estimates the unmixing matrix **W** ≈ **A**⁻¹ by maximising non-Gaussianity of each source (negentropy approximation). The algorithm iterates a fixed-point update on the negentropy gradient.

**Limitations:**
- ICA assumes source statistical independence; maternal and fetal ECG are not perfectly independent. The model is an approximation.
- Component ordering is not guaranteed; downstream classification of components is required.
- Performance degrades when signal-to-noise ratio < 10 dB.

### 4.2 Component Classification (`ComponentAnalyzer`)

Each ICA-recovered component is assigned a label based on its dominant frequency, estimated via FFT in the 0.5–5 Hz band:

| Dominant Frequency | Label |
|-------------------|-------|
| < 1.5 Hz | Unknown (slow artefact) |
| 1.5 – 2.0 Hz | Maternal ECG (90–120 bpm) |
| 2.0 – 2.67 Hz | Fetal ECG (120–160 bpm) |
| > 2.67 Hz | Unknown (fast artefact) |

**Note:** These ranges are heuristic. Overlap exists in cases of maternal tachycardia or fetal bradycardia. Manual review of component waveforms is recommended.

### 4.3 Reconstruction Quality

For each separated component, `SignalSeparator.estimate_quality()` computes:

- **NMSE** (Normalised Mean Square Error): Lower is better; values < 0.05 indicate good reconstruction.
- **Pearson correlation** between original and reconstructed signals.

---

## 5. Feature Extraction (`src/feature_extraction/__init__.py`)

### 5.1 R-Peak Detection

**Method:** Adaptive threshold with minimum distance constraint  
**Threshold:** μ + 2σ of |signal| (where μ, σ are computed over the full segment)  
**Minimum RR distance:** 0.4 s (equivalent to 150 bpm upper limit)

**Performance notes:**
- Threshold multiplier of 2.0 is suitable for clean signals. Noisier signals may require a multiplier of 2.5–3.0.
- `scipy.signal.find_peaks` is used; height and distance constraints filter spurious peaks.

### 5.2 Time-Domain HRV Features

| Feature | Formula | Interpretation |
|---------|---------|----------------|
| `heart_rate_mean` | 60 / (RR̄ / 1000) | Mean heart rate in bpm |
| `heart_rate_std` | std(60 / (RR / 1000)) | HR variability |
| `rr_interval_mean` | mean(RR) ms | Mean RR interval |
| `rr_interval_std` | std(RR) ms | RR variability |
| `rmssd` | √(mean(Δrr²)) ms | Parasympathetic activity proxy |
| `pnn50` | 100 × (|Δrr| > 50 ms) / N % | High-frequency HRV marker |

**Reliability flag:** Features computed from < 30 beats should be treated as unreliable. The pipeline does not apply this flag automatically; downstream users must check `num_beats`.

### 5.3 Frequency-Domain HRV (Notebook 03)

**Method:** Welch Power Spectral Density  
**Window:** Hann, 256 samples  
**Overlap:** 128 samples (50%)  
**Frequency bands:**

| Band | Range | Physiological Meaning |
|------|-------|----------------------|
| Low Frequency (LF) | 0.04 – 0.15 Hz | Sympathetic + parasympathetic tone |
| High Frequency (HF) | 0.15 – 0.40 Hz | Parasympathetic (respiratory) tone |
| LF/HF ratio | — | Sympathovagal balance index |

**Limitation for short segments:** Welch PSD on 10-second segments resolves only down to 0.1 Hz, which is near the LF lower boundary. LF estimates on short ECG segments carry high uncertainty and should be interpreted cautiously.

---

## 6. Maturation Index

The `MaturationIndex` class (see `src/scoring_model/__init__.py`) fuses three HRV sub-scores into a weighted average:

| Feature | Normalisation | Weight |
|---------|---------------|--------|
| `heart_rate_mean` | Binary: 1 if 120–160 bpm, else 0 | 1.0 |
| `rmssd` | Clip((rmssd − 5) / 35, 0, 1) | 1.5 |
| `pnn50` | Clip(pnn50 / 20, 0, 1) | 1.0 |

The weighted average gives a score ∈ [0, 1]. Higher values indicate greater alignment with known markers of fetal autonomic maturity, not a clinical diagnosis.

**Confidence interval:** A 1000-sample bootstrap with Gaussian jitter (σ = 0.03 × |feature value|) is used to produce a 95 % CI. Wide CI (width > 0.3) should be interpreted as high measurement uncertainty.

---

## 7. Database Integration

All pipeline outputs are persisted to a local SQLite database (`data/processed/neuro_genomic.db`):

| Table | Source Notebook | Schema |
|-------|----------------|--------|
| `raw_ecg` | External / bootstrapped | timestamp, channel, amplitude |
| `separated_components` | Notebook 02 | time, maternal, fetal |
| `hrv_feature_matrix` | Notebook 03 | signal_name, feature columns, computed_at |

---

## 8. Reproducibility Checklist

- [x] All random seeds fixed (`random_state=42`, `np.random.default_rng(42)`)
- [x] Filter parameters documented and version-pinned via `requirements.txt`
- [x] Synthetic data generation is deterministic given fixed seed
- [x] All notebooks are unexecuted on commit (clean state); run in order 01 → 02 → 03 → exploration

---

## 9. Known Limitations

1. **Synthetic data only:** The pipeline has not been validated on real clinical ECG recordings.
2. **Short signal segments:** 10 s segments limit frequency-domain HRV reliability.
3. **ICA component ambiguity:** In low-SNR conditions, maternal and fetal components may be mixed or misordered.
4. **No external validation:** Maturation index weights are based on literature heuristics; no empirical calibration on labelled data has been performed.
5. **Single-subject prototype:** The pipeline processes one signal record at a time; batch processing and population-level normalization are not yet implemented.
