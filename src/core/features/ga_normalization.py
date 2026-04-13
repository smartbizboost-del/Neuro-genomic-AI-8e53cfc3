# src/core/features/ga_normalization.py

# FANTE protocol cut-offs (from University of Pisa study)
GA_THRESHOLDS = {
    '23-26w': {'RMSSD': 2.4, 'HF': 1.5, 'LF/HF': 7.0},
    '27-30w': {'RMSSD': 3.2, 'HF': 2.1, 'LF/HF': 6.5},
    '31-34w': {'RMSSD': 4.0, 'HF': 2.8, 'LF/HF': 6.0},
    '35-38w': {'RMSSD': 4.8, 'HF': 3.5, 'LF/HF': 5.5},
}

def get_ga_bin(gestational_weeks):
    """Return GA bin for threshold lookup"""
    if gestational_weeks < 27:
        return '23-26w'
    elif gestational_weeks < 31:
        return '27-30w'
    elif gestational_weeks < 35:
        return '31-34w'
    else:
        return '35-38w'

def normalize_by_ga(features, gestational_weeks):
    """Normalize HRV features using GA-specific thresholds"""
    ga_bin = get_ga_bin(gestational_weeks)
    thresholds = GA_THRESHOLDS[ga_bin]

    normalized = {}
    for key, value in features.items():
        if key in thresholds:
            normalized[key] = value / thresholds[key]
        else:
            normalized[key] = value
    return normalized