# PhysioNet Database Guide

## Overview

PhysioNet (https://physionet.org/) maintains a collection of open-access physiological signal databases widely used in biomedical research and machine learning development.

## Recommended Databases for This Project

### 1. **Abdominal and Direct Fetal ECG Database** ⭐ BEST FOR FETAL ANALYSIS

**Purpose**: Maternal-fetal ECG recordings with direct fetal lead  
**Link**: https://physionet.org/content/aami-ec13/1.0/  
**Format**: WFDB (standard PhysioNet format)

**What's Included:**
- Multi-channel abdominal maternal ECG
- Direct fetal ECG (from scalp electrode)
- Simultaneous maternal reference lead
- Reference beat annotations (R-peak locations)
- Multiple subjects across different gestational ages

**Key Statistics:**
- Sampling rate: 1000 Hz
- Channels: 4 (2+ abdominal, 1 direct fetal, 1 maternal)
- Duration: 30-60 minutes per recording
- Number of subjects: 38
- Free to download and use

**How to Load:**
```python
import wfdb

# List available records
db = wfdb.get_record_list('adf-termdata')

# Load specific record
record = wfdb.rdrecord('adf-termdata/adf_13')

signal = record.p_signal  # Shape: (n_samples, n_channels)
fs = record.fs  # Sampling frequency
comments = record.comments  # Metadata
```

---

### 2. **MIT-BIH Arrhythmia Database** (Adult ECG)

**Purpose**: Reference adult ECG for algorithm development  
**Link**: https://physionet.org/content/mitdb/1.0.0/

**Key Statistics:**
- 47 records from 47 patients
- 30 minutes each at 360 Hz
- 2 channels each
- Well-annotated beat locations

**Use Case**: Validate preprocessing and detection algorithms

---

### 3. **LTDB (Long-Term Database)**

**Purpose**: Extended continuous monitoring for HRV analysis  
**Link**: https://physionet.org/content/ltdb/1.0.0/

**Key Statistics:**
- 84 long-term ECG recordings
- 24 hours continuous
- 128 Hz sampling rate

**Use Case**: Study of temporal HRV patterns and circadian rhythms

---

## How to Download and Use PhysioNet Data

### Method 1: Using WFDB Python Library (Recommended)

```python
# Install library
pip install wfdb

# List available databases
import wfdb
records = wfdb.get_record_list('adf-termdata')
print(records)  # Shows all record names

# Download and load a record
record = wfdb.rdrecord('adf-termdata/adf_13')
signal = record.p_signal
fs = record.fs
annotations = wfdb.rdann('adf-termdata/adf_13', 'atr')  # Load annotations
```

### Method 2: Manual Download

1. Visit https://physionet.org/
2. Select database
3. Download data files (.dat, .hea)
4. Place in `data/raw/physionet/` directory
5. Load as shown above

### Method 3: Google Colab (Cloud-Based)

```python
# In Colab, download directly
import os
import subprocess

# Create data directory
os.makedirs('/content/physionet_data', exist_ok=True)

# Download specific record
subprocess.run([
    'wget', '-r', '-N',
    'https://physionet.org/files/adf-termdata/1.0.0/adf_13.dat',
    '-P', '/content/physionet_data'
])

# Load
import wfdb
record = wfdb.rdrecord('/content/physionet_data/adf-termdata-1.0.0/adf_13')
```

---

## Data Structure

PhysioNet WFDB files come as pairs:

- **`.hea`** - Header file (metadata)
  - Sampling rate
  - Number of channels
  - Signal names
  - Physical units

- **`.dat`** - Binary data file (16-bit samples)
  - Raw signal values
  - One or more channels

### Example Header File Content:
```
adf_13 4 1000 64000
adf_13.dat 16 0 0 -2048 0 0 0 ECG I
adf_13.dat 16 16 0 -2048 0 0 0 ECG II
adf_13.dat 16 32 0 -2048 0 0 0 Abdominal ECG
adf_13.dat 16 48 0 -2048 0 0 0 Direct Fetal ECG

# Other annotations
```

---

## Loading and Processing PhysioNet Data in This Project

### Step 1: Download Database

```python
import wfdb

# Download abdominal-fetal database
database_name = 'adf-termdata'
records = wfdb.get_record_list(database_name)

for record_name in records[:5]:  # First 5 records
    try:
        record = wfdb.rdrecord(f'{database_name}/{record_name}')
        print(f"Downloaded: {record_name}, Shape: {record.p_signal.shape}")
    except Exception as e:
        print(f"Error downloading {record_name}: {e}")
```

### Step 2: Preprocess

```python
from src.preprocessing import ECGPreprocessor

preprocessor = ECGPreprocessor(sampling_rate=1000, lowcut=0.5, highcut=40)

for record_name in records:
    record = wfdb.rdrecord(f'{database_name}/{record_name}')
    
    # Filter signal
    filtered = preprocessor.filter_signal(record.p_signal)
    
    # Save processed data
    np.save(f'data/processed/{record_name}_filtered.npy', filtered)
```

### Step 3: Separation and Analysis

```python
from src.signal_separation import SignalSeparator
from src.feature_extraction import HRVExtractor

separator = SignalSeparator(n_components=2)
extractor = HRVExtractor(sampling_rate=1000)

components = separator.fit_transform(filtered)
features = extractor.extract_batch_features({
    'IC1': components[:,0],
    'IC2': components[:,1]
})

print(f"IC1 Heart Rate: {features['IC1']['heart_rate_mean']:.1f} bpm")
print(f"IC2 Heart Rate: {features['IC2']['heart_rate_mean']:.1f} bpm")
```

---

## Data Processing Pipeline

```
PhysioNet Database
        ↓
  Download (wfdb)
        ↓
  ECG Preprocessing
  (Filtering, Normalization)
        ↓
  Signal Separation (ICA)
        ↓
  Feature Extraction (HRV)
        ↓
  Save to data/processed/
        ↓
  Ready for ML Models
```

---

## File Organization

```
data/
├── raw/
│   └── physionet/
│       ├── adf_13.dat
│       ├── adf_13.hea
│       ├── adf_14.dat
│       ├── adf_14.hea
│       └── ...
├── processed/
│   ├── adf_13_filtered.npy
│   ├── adf_13_separated.npy
│   ├── adf_13_features.json
│   └── ...
└── features/
    ├── training_features.csv
    └── labels.csv
```

---

## Important Notes

### License
**Cite when publishing:**

```
Goldberger, A. L., Amaral, L. A., Glass, L., Hausdorff, J. M., Ivanov, P. C., 
Mark, R. G., ... & Stanley, H. E. (2000). PhysioBank, PhysioToolkit, and PhysioNet: 
Components of a new research resource for complex physiologic signals. Circulation, 
101(23), e215-e220.
```

### Data Ethics
- All data is de-identified (HIPAA compliant)
- Free for research and education
- Respect publication policies

### Validation
Always compare your results with:
- Published ground truth annotations
- Clinical reference measurements
- Peer-reviewed validation studies

---

## Next Steps

1. **Download first record**: `adf_13` (well-documented, good quality)
2. **Run preprocessing notebook**: `01_signal_preprocessing_and_analysis.ipynb`
3. **Compare results** with ground truth annotations
4. **Validate component separation** against clinician assessment
5. **Build aggregate dataset** from multiple subjects

---

**Last Updated**: March 5, 2026  
**For Questions**: See `docs/research_notes/` for detailed analysis logs
