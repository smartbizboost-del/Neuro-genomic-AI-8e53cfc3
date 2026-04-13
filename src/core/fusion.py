# src/core/fusion.py
def fuse_with_doppler(hrv_features, doppler_fhr):
    """Combine HRV features with Doppler fetal heart rate"""
    # Simple weighted average or more complex fusion
    combined_risk = 0.7 * hrv_features['risk_score'] + 0.3 * normalize_doppler(doppler_fhr)
    return combined_risk

def normalize_doppler(doppler_fhr):
    """Normalize Doppler FHR to risk score"""
    # Placeholder normalization
    return (doppler_fhr - 120) / 20  # Example