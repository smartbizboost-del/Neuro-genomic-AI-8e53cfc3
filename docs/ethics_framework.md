# Ethics Framework — Neuro-Genomic AI Research Prototype

> **Document type:** Research ethics alignment  
> **Version:** 1.0 | March 2026  
> **Status:** Research prototype — NOT for clinical or commercial deployment

---

## 1. Overview

This document maps every technical component of the Neuro-Genomic AI pipeline to a corresponding ethical safeguard. The framework follows the principles of the Belmont Report (Respect for Persons, Beneficence, Justice) and is informed by IEEE Ethically Aligned Design and the EU AI Act risk classification guidelines.

The system is classified as a **high-risk research tool** under internal review because it processes multi-modal biological data (physiological signals, genomic variants, behavioral metrics) relating to fetal development. All outputs are strictly for research exploration and must never be used in clinical settings without independent regulatory approval.

---

## 2. Ethical Principles

| Principle | Implementation |
|-----------|----------------|
| Respect for Persons | All data samples are synthetic or anonymised. No personally identifiable information (PII) is stored. Informed consent protocols are documented for any future prospective study. |
| Beneficence | The research goal is to advance scientific understanding of fetal maturation; potential knowledge benefits are described in the proposal. No individual-level harm is introduced by algorithmic outputs. |
| Non-Maleficence | Clinical decision-making is explicitly excluded. All outputs carry mandatory disclaimers. No clinical thresholds are encoded into any model. |
| Justice | No automated selection or screening of individuals. Feature importance analysis is required so biases in model decisions can be inspected and reported. |
| Transparency | All model parameters, training procedures, and limitations are documented in the signal processing report and paper draft. |
| Accountability | A named research contact is required before this prototype is shared externally. All code is versioned. |

---

## 3. Pipeline Component Mapping

### 3.1 Data Acquisition & Storage

| Risk | Safeguard |
|------|-----------|
| Sensitive genomic data exposure | Data is stored in a local SQLite database (`neuro_genomic.db`). No cloud upload without explicit consent and encryption. |
| Re-identification of synthetic data | Synthetic records are generated with no traceable individual parameters. |
| Data integrity | All ingested data is validated for schema compliance before insertion into the database. |
| Access control | Database file permissions follow least-privilege principle. No web-accessible endpoints. |

### 3.2 Signal Preprocessing (`src/preprocessing/`)

| Risk | Safeguard |
|------|-----------|
| Filter artefacts misrepresented as clinical findings | Filter parameters (Butterworth 0.5–40 Hz, order 4) are documented and justified. Filtered signals are not reported as diagnostic-grade. |
| Loss of signal quality undetected | Signal quality metrics are computed and displayed in the demo interface before any analysis is shown. |
| Overfitting to artefactual data | Synthetic ECG used for development; real physiological signals must undergo independent quality review before use. |

### 3.3 Signal Separation — FastICA (`src/signal_separation/`)

| Risk | Safeguard |
|------|-----------|
| Incorrect maternal/fetal component labelling | Component frequency classification is heuristic-based and labelled as "estimated." Results include frequency and confidence indicators. |
| Algorithmic bias in ICA | Fixed random seed (`random_state=42`) for reproducibility. Component labelling is logged and reviewable. |
| False confidence in component identity | Reconstruction quality metrics (NMSE, correlation) are computed and reported. |

### 3.4 Feature Extraction — HRV (`src/feature_extraction/`)

| Risk | Safeguard |
|------|-----------|
| HRV features misused for clinical diagnosis | Feature outputs are labelled as "research metrics." All feature tables include a metadata flag: `research_use_only=True`. |
| R-peak detection errors propagating silently | R-peak count and detection confidence are reported alongside HRV features. |
| Frequency-domain estimates on short segments | Welch PSD window parameters are documented. Features computed on <30 beats are flagged as unreliable. |

### 3.5 Maturation Index (`src/scoring_model/`)

| Risk | Safeguard |
|------|-----------|
| Score interpreted as clinical gestational age | The index is explicitly bounded [0, 1] with no gestational age labels or clinical cut-offs. Mandatory disclaimer is embedded in every output dict. |
| Overconfident score | Bootstrap 95 % confidence interval is always returned alongside the point estimate. Wide CI triggers a "high uncertainty" flag in the demo interface. |
| Hidden clinical thresholds | No threshold-based decisions are implemented. All colour coding in visualisation uses neutral research palettes. |
| Model performance claims without validation | The ML scorer (`MaturationScorer`) reports MAE and R² on a held-out test set only. No external validation claims are made. |

### 3.6 HCI Demo Interface (`notebooks/04_demo_interface.ipynb`)

| Risk | Safeguard |
|------|-----------|
| Clinician misuse | Interface header contains a bold, non-dismissible disclaimer. |
| Data entered by non-researchers | Input section includes a usage context reminder. |
| Visual design implying clinical precision | Colour scale uses blue/grey (not red/green clinical traffic-light). CI uncertainty bar is displayed prominently. |

---

## 4. Data Governance

### 4.1 Data Types Used

| Data Domain | Sensitivity Level | Storage | Retention |
|-------------|-------------------|---------|-----------|
| Physiological (ECG, EDA, respiration) | High | Local SQLite only | Research duration |
| Genomic (gene expression, variant load) | Very High | Local SQLite only | Research duration |
| Behavioral (click rate, typing speed) | Medium | Local SQLite only | Research duration |

### 4.2 Anonymisation

All data in the current prototype is fully synthetic (generated by `DataPipeline.bootstrap_local_database()`). No real patient data is included. Should real data be incorporated in a future study:
- Data must be de-identified per HIPAA Safe Harbor or equivalent standard.
- Genomic data requires additional IRB / ethics board approval.
- A Data Management Plan (DMP) must be filed and approved before data collection.

### 4.3 Third-Party Dependencies

| Library | Version Pin | Audit Status |
|---------|-------------|--------------|
| scikit-learn | ≥1.3 | No known critical CVEs |
| scipy | ≥1.11 | No known critical CVEs |
| numpy | ≥1.25 | No known critical CVEs |
| pandas | ≥2.0 | No known critical CVEs |

---

## 5. Bias & Fairness Assessment

- **Population representativeness:** Synthetic data does not reflect any demographic group. Real-data studies must include demographic analysis.
- **Feature selection bias:** HRV features were selected based on published literature; selection rationale is documented in the signal processing report.
- **Outcome variable bias:** The maturation index uses no binary clinical categories. Gestational age regression in `MaturationScorer` must document training data demographics if ever deployed.

---

## 6. Incident Response

In the event that this tool's outputs are misused in a clinical context:
1. Immediately notify the principal investigator.
2. Withdraw the tool from all shared environments.
3. Document the incident, contributing factors, and corrective actions.
4. Review and strengthen disclaimers and access controls before any re-deployment.

---

## 7. Approvals & Review

| Role | Responsibility |
|------|----------------|
| Principal Investigator | Approves research design and data governance decisions |
| Ethics Board / IRB | Required before any real human subject data is collected |
| Independent Technical Reviewer | Reviews model outputs and feature importance before publication |
| Data Protection Officer | Reviews data storage and anonymisation approach |

---

*This document should be reviewed and updated at each major version release of the pipeline.*
