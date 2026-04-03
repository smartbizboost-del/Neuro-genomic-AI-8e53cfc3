# Neuro-Genomic AI — Demo Presentation

> **Document type:** Presentation outline + speaker notes  
> **Version:** 1.0 | March 2026  
> **Audience:** Research group, academic peers, project supervisors

---

## Slide 1 — Title

**Neuro-Genomic AI**  
*A Multi-Modal Research Prototype for Fetal Autonomic Maturation Analysis*

March 2026 | Research Prototype v1.0

> **Speaker note:** Open with a short framing statement: *"This is a research exploration tool — not a clinical product."* Emphasise the academic purpose immediately.

---

## Slide 2 — Motivation

**Why does fetal autonomic maturation matter?**

- The fetal autonomic nervous system (ANS) matures rapidly between weeks 20–40 of gestation.
- ANS maturity is reflected in Heart Rate Variability (HRV) — measurable, non-invasive.
- Poor autonomic development correlates with adverse neurodevelopmental outcomes.
- Current tools either require invasive monitoring or lack rigorous uncertainty quantification.

**Research gap:**  
→ No open, reproducible multi-modal analysis pipeline exists to explore HRV-based maturation proxies in a controlled research setting.

---

## Slide 3 — What We Built

**A 5-stage end-to-end pipeline:**

```
Raw ECG (mixed) 
  → Preprocessing (Butterworth filter)
  → Signal Separation (FastICA)
  → HRV Feature Extraction
  → Maturation Index [0–1] + 95% CI
```

Plus: multi-modal integration (genomic + behavioral data), SQLite database backend, ethics framework, reproducible notebooks.

---

## Slide 4 — System Architecture Diagram

```
┌──────────────────────────────────────────────┐
│                Data Sources                  │
│  [ECG] [Genomic] [Behavioral]                │
└─────────────────┬────────────────────────────┘
                  ↓
┌──────────────────────────────────────────────┐
│           SQLite Database                    │
│      neuro_genomic.db (local)                │
└─────────────────┬────────────────────────────┘
                  ↓
┌──────────────────────────────────────────────┐
│        src/ Python Modules                   │
│  preprocessing → signal_separation           │
│  → feature_extraction → scoring_model        │
└─────────────────┬────────────────────────────┘
                  ↓
┌──────────────────────────────────────────────┐
│           Jupyter Notebooks                  │
│  01_preprocessing → 02_separation            │
│  → 03_features → 04_demo                     │
└──────────────────────────────────────────────┘
```

> **Speaker note:** Highlight the unidirectional data flow — each stage reads from the DB and writes results back. This ensures reproducibility.

---

## Slide 5 — Signal Processing: Preprocessing

**Challenge:** Raw ECG contains maternal and fetal signals mixed together.

**Solution:**
- Butterworth bandpass filter (0.5–40 Hz, 4th order, zero-phase)
- Lower bound: removes breathing artefacts + electrode drift
- Upper bound: suppresses maternal muscle noise (EMG)
- Zero-phase: no timing shift (critical for R-peak accuracy)

> **Show:** Raw vs filtered ECG comparison plot from Notebook 01.

---

## Slide 6 — Signal Processing: FastICA Separation

**Fast Independent Component Analysis (ICA)**

- Assumes maternal + fetal ECG are statistically independent sources.
- Solves: **x = As** → estimate unmixing matrix **W ≈ A⁻¹**
- Result: 2 independent components — one for each cardiac source.

**Component identification:**
- Maternal: dominant frequency 1.5–2.0 Hz (~90–120 bpm)
- Fetal: dominant frequency 2.0–2.67 Hz (~120–160 bpm)

> **Show:** ICA component plot from Notebook 02.

---

## Slide 7 — HRV Feature Extraction

**Time-domain features from RR intervals:**

| Feature | What it measures |
|---------|-----------------|
| RMSSD | Parasympathetic (vagal) tone |
| pNN50 | High-frequency HRV activity |
| Heart rate mean | Average fetal HR |
| LF/HF ratio | Sympathovagal balance |

**Reliability check:** Features flagged as unreliable if < 30 beats detected.

> **Show:** Feature matrix table from Notebook 03.

---

## Slide 8 — The Maturation Index

**Fusing HRV features into a single research-grade index:**

$$M = \frac{1.0 \cdot s_{HR} + 1.5 \cdot s_{RMSSD} + 1.0 \cdot s_{pNN50}}{3.5}$$

Where each $s_i \in [0, 1]$ is a normalized feature sub-score.

**Always includes:**
- 95% Bootstrap Confidence Interval
- Uncertainty width indicator
- Mandatory Research Disclaimer

> **IMPORTANT:** M is NOT gestational age. It is a normalized research index — no clinical thresholds, no diagnostic categories.

---

## Slide 9 — Demo Interface

**Live demo: `notebooks/04_demo_interface.ipynb`**

Key sections:
1. Load HRV features from DB (or enter manually)
2. View signal quality indicators
3. See maturation index + CI visualization
4. Read uncertainty note + disclaimer

> **Demo note:** Scroll to the uncertainty bar visualization. Point out: "The system never shows just a number — it always shows 'how confident should you be in this number.'"

---

## Slide 10 — Ethics Framework Highlights

Full documentation: `docs/ethics_framework.md`

| Component | Key Safeguard |
|-----------|--------------|
| Data storage | Local SQLite only, no cloud |
| Genomic data | Very High sensitivity — IRB required for real data |
| Maturation index | No clinical thresholds; CI always shown |
| Interface design | Non-dismissible disclaimer; neutral colour palette |
| Accountability | Named PI required before external sharing |

**Prototype is classified as high-risk research tool — not AI Act "minimal risk."**

---

## Slide 11 — Current Limitations

Be transparent about what the prototype cannot do:

1. Only tested on synthetic data — no clinical validation.
2. 10-second ECG segments limit LF/HF reliability.
3. ICA component labelling is heuristic — can fail in pathological cases.
4. No gestational age calibration.
5. Single-subject processing only; no population normalization.

> **Speaker note:** Limitations build trust. Acknowledging them shows rigour and prepares the audience for future work.

---

## Slide 12 — Future Research Directions

- Validate on PhysioNet clinical databases (ADFECGDB, NInFEA).
- Incorporate genomic expression features (APOE, BDNF, SLC6A4) into model.
- Longitudinal tracking: week-over-week maturation curves.
- Formal IRB study with de-identified clinical data.
- Submit for ethics board review under EU MDR / FDA AI/ML guidance.

---

## Slide 13 — Repository Tour

```
neuro-genomic-ai/
├── notebooks/         # Execution pipeline (run in order)
│   ├── 01_signal_preprocessing_and_analysis.ipynb
│   ├── 02_signal_separation.ipynb
│   ├── 03_feature_extraction.ipynb
│   ├── 04_demo_interface.ipynb
│   └── exploration.ipynb
├── src/               # Core Python modules
│   ├── data_pipeline.py
│   ├── preprocessing/
│   ├── signal_separation/
│   ├── feature_extraction/
│   └── scoring_model/
├── docs/              # Research documentation
│   ├── ethics_framework.md
│   ├── signal_processing_report.md
│   ├── paper_draft.md
│   └── presentation.md
└── README.md
```

---

## Slide 14 — Summary

- End-to-end multi-modal pipeline: ECG → HRV → Maturation Index
- FastICA maternal-fetal separation with quality metrics
- Bootstrap confidence intervals on all index estimates
- Comprehensive ethics framework with per-component safeguards
- Reproducible, documented, open codebase

**This is a stepping stone toward rigorous, ethically grounded fetal neurodevelopmental research.**

---

## FAQ

**Q: Can clinicians use this tool?**  
A: No. It is a research prototype. No clinical use without independent validation and regulatory clearance.

**Q: Why synthetic data?**  
A: We do not have IRB approval for real fetal ECG in this phase. Synthetic data allows us to build and validate the pipeline architecture.

**Q: How were the maturation index feature weights chosen?**  
A: Based on literature-derived physiological principles (RMSSD weighted more heavily as the most established marker). Empirical calibration requires a labeled clinical dataset — planned for future work.

**Q: Is the genomic data used in the maturation index?**  
A: Not in the current index. Genomic features (gene expression, variant load) are loaded and explored in `exploration.ipynb` but not yet fused into the scoring model. Multi-modal fusion is future work.

**Q: What makes this "ethically grounded"?**  
A: Every component maps to a documented safeguard. The tool never makes clinical decisions. CI is always shown. The disclaimer is embedded in every output.

**Q: How do I reproduce the results?**  
A: Run notebooks in order (01 → 02 → 03 → 04). The DB is auto-bootstrapped from synthetic data on first run. See `README.md` for setup.

---

*Presentation prepared for research group seminar and project submission. March 2026.*
