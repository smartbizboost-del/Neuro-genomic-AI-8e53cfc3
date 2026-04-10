# Neuro-Genomic AI: Detailed Project Presentation

Version: March 2026
Audience: Research seminar, supervisors, technical reviewers
Status: Research prototype (non-clinical)

---

## Slide 1 - Title

Neuro-Genomic AI
Detailed End-to-End Pipeline for Fetal Autonomic Maturation Research

Key message:
- This project is a reproducible research system that converts mixed ECG and multi-modal context data into a maturation class prediction and uncertainty-aware analysis outputs.

---

## Slide 2 - Why This Project Exists

Problem context:
- Fetal autonomic nervous system maturation is linked to neurodevelopment outcomes.
- ECG-based heart rate variability (HRV) can capture autonomic patterns non-invasively.
- Raw fetal/maternal ECG is mixed and noisy, so direct interpretation is difficult.

Research objective:
- Build a transparent, modular, reproducible pipeline that:
1. Separates maternal/fetal signals.
2. Extracts robust HRV features.
3. Trains a single best model for maturation classification.
4. Produces a practical prediction workflow.

---

## Slide 3 - Full System At A Glance

Data flow overview:

1. Input data
- Physiological CSV (ECG and related signals)
- Genomic CSV
- Behavioral CSV

2. Data persistence
- SQLite database at data/processed/neuro_genomic.db

3. Signal processing pipeline
- Filtering -> ICA separation -> HRV feature extraction

4. Modeling pipeline
- NeuralNetwork classifier training/evaluation
- Saved production model artifact

5. Inference pipeline
- Load saved model
- Predict maturation class from extracted features
- Return class probabilities

---

## Slide 4 - Repository Architecture

Main directories and roles:

- notebooks/
1. 01_signal_preprocessing_and_analysis.ipynb
2. 02_signal_separation.ipynb
3. 03_feature_extraction.ipynb
4. 04_demo_interface.ipynb
5. 05_neural_network_model_selection.ipynb

- src/
1. data_pipeline.py: DB-first ingestion and table loading
2. preprocessing/: filtering and basic signal cleaning
3. signal_separation/: source separation logic
4. feature_extraction/: HRVExtractor and derived features
5. model.py: CognitiveStateClassifier (supports nn mode)
6. scoring_model/: maturation index utilities

- docs/
1. ethics framework
2. signal processing report
3. paper draft
4. this presentation

- results/models/
1. best_maturation_classifier.pkl
2. model_evaluation_report.csv

---

## Slide 5 - Notebook Execution Order

Operational order to run the project:

1. Notebook 01
- Preprocess and inspect signals
- Validate filtering and initial signal quality

2. Notebook 02
- Apply separation pipeline
- Persist separated components to DB

3. Notebook 03
- Extract HRV features from separated components
- Persist feature matrix to DB table hrv_feature_matrix

4. Notebook 05
- Load extracted features from DB
- Train and evaluate NeuralNetwork model
- Save model and generate prediction

5. Notebook 04
- Demonstration and visualization layer for reporting

Important:
- Notebook 05 is now DB-only for feature loading (no CSV/synthetic fallback in strict mode).

---

## Slide 5A - Stage-Based File Tree (Data Processing -> Model Training)

```text
neuro-genomic-ai-main/
|
+-- Stage 1: Data Ingestion
|   |
|   +-- src/data_pipeline.py
|   +-- src/train_from_physionet.py
|   +-- data/processed/neuro_genomic.db
|       +-- physio_data
|       +-- genomic_data
|       +-- behavioral_data
|
+-- Stage 2: Signal Processing
|   |
|   +-- src/preprocessing/__init__.py
|   +-- src/signal_separation/__init__.py
|   +-- notebooks/01_signal_preprocessing_and_analysis.ipynb
|   +-- notebooks/02_signal_separation.ipynb
|   +-- data/processed/neuro_genomic.db
|       +-- separated_components
|
+-- Stage 3: Feature Extraction
|   |
|   +-- src/feature_extraction/__init__.py
|   +-- notebooks/03_feature_extraction.ipynb
|   +-- data/processed/neuro_genomic.db
|       +-- hrv_feature_matrix
|
+-- Stage 4: Model Training (Best Model Only)
|   |
|   +-- src/model.py
|   +-- src/train_from_physionet.py
|   +-- notebooks/05_neural_network_model_selection.ipynb
|   +-- results/models/best_maturation_classifier.pkl
|   +-- results/models/model_evaluation_report.csv
|
+-- Stage 5: Prediction and Demo
    |
    +-- notebooks/05_neural_network_model_selection.ipynb
    +-- notebooks/04_demo_interface.ipynb
```

How to explain this slide:
1. Stages 1 to 3 create trustworthy features in the database.
2. Stage 4 trains the NeuralNetwork only on extracted HRV features.
3. Stage 5 uses the saved model artifact for prediction.

---

## Slide 6 - Step 1: Data Ingestion and Storage

How data enters the system:

- Input CSV files are loaded through pipeline utilities.
- Tables are written to SQLite for reproducibility and traceability.
- Downstream notebooks read from DB instead of ad hoc in-memory data.

Why this design matters:
- Guarantees a consistent source of truth.
- Makes reruns deterministic.
- Simplifies debugging and auditing.

Core DB entities used by modeling path:
- separated_components
- hrv_feature_matrix

---

## Slide 7 - Step 2: Signal Preprocessing

Goal:
- Improve ECG quality before decomposition and peak analysis.

Typical operations:
1. Bandpass filtering to remove baseline drift and high-frequency noise.
2. Normalization to stabilize decomposition and feature extraction.

Outcome:
- Cleaner mixed signals ready for source separation.

---

## Slide 8 - Step 3: Maternal/Fetal Signal Separation

Method:
- FastICA separates mixed observations into statistically independent components.

Result:
- Two reconstructed channels interpreted as maternal and fetal ECG components.

Persistence:
- Components are stored in DB table separated_components for downstream extraction.

Why this is critical:
- HRV features for fetal analysis are unreliable without robust separation.

---

## Slide 9 - Step 4: HRV Feature Extraction

Source:
- Reads separated maternal/fetal ECG components.

Process:
1. Detect R-peaks.
2. Compute RR intervals.
3. Derive time-domain features.

Key features used for modeling:
- mat_heart_rate_mean
- mat_rmssd
- mat_pnn50
- fet_heart_rate_mean
- fet_rmssd
- fet_pnn50

Output:
- Feature rows saved into hrv_feature_matrix.

---

## Slide 10 - Step 5: Dataset Construction for Learning

Inside notebook 05:

1. Load required columns from DB-derived feature matrix.
2. Validate no missing required feature columns.
3. Build supervised training frame using extracted-feature rows.
4. Generate target maturation classes from weighted continuous maturity score using quantile bins:
- low_maturity
- mid_maturity
- high_maturity

Reason for quantile binning:
- Ensures class separation for training/evaluation while preserving feature-driven ordering.

---

## Slide 11 - Step 6: Model Selection Simplified to Best Model

Current production choice:
- Keep only NeuralNetwork (MLP-based classifier).

What was changed:
- Multi-model comparison path removed from active workflow.
- Training cell now instantiates and fits only CognitiveStateClassifier(model_type='nn').

Evaluation retained:
1. Holdout Accuracy
2. Holdout weighted F1
3. Confusion matrix
4. ROC-AUC (weighted OVR)
5. 5-fold stratified CV metrics

---

## Slide 12 - Step 7: Model Saving and Artifacts

Model artifact:
- results/models/best_maturation_classifier.pkl

Evaluation artifact:
- results/models/model_evaluation_report.csv

Saved report fields include:
- model
- accuracy
- f1_weighted
- cv_f1_weighted_mean
- cv_f1_weighted_std
- cv_accuracy_mean
- cv_accuracy_std
- roc_auc_ovr_weighted

Why this is useful:
- Separates training runtime from inference runtime.
- Enables reproducible handoff to demo/inference scripts.

---

## Slide 13 - Step 8: Prediction Workflow

Prediction path in notebook 05:

1. Load the saved model from best_maturation_classifier.pkl.
2. Build a one-row feature input with the same six required columns.
3. Predict class label.
4. Predict per-class probabilities.

Example output shape:
- Predicted class: mid_maturity
- Probability distribution:
1. low_maturity: p
2. mid_maturity: p
3. high_maturity: p

Inference contract:
- Input schema must exactly match the six required feature names and numeric types.

---

## Slide 14 - How Components Connect (File-Level)

Execution dependency chain:

1. notebooks/03_feature_extraction.ipynb
- Produces hrv_feature_matrix in DB

2. notebooks/05_neural_network_model_selection.ipynb
- Reads DB features
- Builds supervised dataset
- Trains NeuralNetwork
- Saves model and report
- Performs sample prediction

3. src/model.py
- Provides CognitiveStateClassifier
- Handles fit/predict and wrapped estimator

4. results/models/*
- Stores deployed model artifact and evaluation summary

Practical implication:
- If DB tables are missing, notebook 05 correctly fails early with clear error messages.

---

## Slide 15 - Validation Snapshot

Observed performance from latest run:

- Holdout Accuracy: ~0.99
- Holdout Weighted F1: ~0.99
- ROC-AUC (weighted OVR): ~0.9997
- CV weighted F1 mean: ~0.9926

Interpretation:
- The current synthetic/derived dataset is highly separable.
- Metrics are suitable for prototype validation, not clinical claims.

---

## Slide 16 - Constraints and Risks

Current limitations:
1. Dataset is synthetic/derived; real-world generalization is unknown.
2. Class targets are engineered from feature score bins.
3. Clinical thresholding is intentionally absent.
4. Domain shift risk is high when moving to clinical ECG.

Mitigation roadmap:
1. External validation on curated datasets.
2. Calibration and uncertainty analysis on real cohorts.
3. Formal ethics and regulatory review before any translational use.

---

## Slide 17 - Reproducibility Checklist

To reproduce fully:

1. Install requirements.
2. Run notebooks 01 -> 02 -> 03 to populate DB.
3. Run notebook 05 to train, evaluate, save, and predict.
4. Verify generated files in results/models/.

Sanity checks:
- DB exists at data/processed/neuro_genomic.db.
- hrv_feature_matrix contains non-empty rows.
- best_maturation_classifier.pkl is generated.

---

## Slide 18 - Final Takeaway

What this project demonstrates:

- A complete research pipeline from raw physiological signal to deployable prediction artifact.
- Strong modularity across ingestion, processing, extraction, modeling, and inference.
- Transparent NeuralNetwork-only prediction path aligned with current best observed performance.

Closing statement:
- This is a robust research foundation for future clinically validated fetal maturation modeling.

---

## Appendix - Database Rows and Columns Used

Database file:
- data/processed/neuro_genomic.db

Current tables:
1. `physio_data`
2. `genomic_data`
3. `behavioral_data`
4. `separated_components`
5. `hrv_feature_matrix`

Row counts:
1. `physio_data`: 650000
2. `genomic_data`: 650
3. `behavioral_data`: 650
4. `separated_components`: 650000
5. `hrv_feature_matrix`: 180

Column schema:

1. `physio_data` (used for ingestion + preprocessing)
- sample_index
- time_sec
- MLII
- V5
- record_name
- database
- sampling_rate

2. `genomic_data` (context table)
- sample_id
- gene_expression_a
- gene_expression_b
- gene_expression_c
- variant_load

3. `behavioral_data` (context table)
- task_id
- click_rate
- typing_speed
- error_rate
- focus_score

4. `separated_components` (used for feature extraction)
- sample_index
- time_sec
- maternal_ecg
- fetal_ecg
- maternal_component_index
- fetal_component_index
- maternal_component_freq_hz
- fetal_component_freq_hz

5. `hrv_feature_matrix` (used for model training)
- window_start
- window_end
- mat_heart_rate_mean
- mat_rmssd
- mat_pnn50
- fet_heart_rate_mean
- fet_rmssd
- fet_pnn50
- mat_num_beats
- fet_num_beats
- target

Training columns currently used by the NeuralNetwork:
1. mat_heart_rate_mean
2. mat_rmssd
3. mat_pnn50
4. fet_heart_rate_mean
5. fet_rmssd
6. fet_pnn50

Target column:
1. target

Current count summary:
1. physio_data: rows 650000, columns 7
2. genomic_data: rows 650, columns 5
3. behavioral_data: rows 650, columns 5
4. separated_components: rows 650000, columns 8
5. hrv_feature_matrix: rows 180, columns 11