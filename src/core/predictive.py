import numpy as np
from sklearn.linear_model import LinearRegression
from typing import List, Dict, Any


def predict_developmental_trajectory(
        historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Predict future developmental index based on historical trends."""
    weeks = np.array([d['gestational_weeks']
                     for d in historical_data]).reshape(-1, 1)
    dev_indices = np.array([d['developmental_index'] for d in historical_data])

    model = LinearRegression()
    model.fit(weeks, dev_indices)

    future_weeks = np.array([[weeks[-1][0] + 2], [weeks[-1][0] + 4]])
    predictions = model.predict(future_weeks)

    trend = 'increasing' if float(model.coef_[0]) > 0 else 'decreasing'
    return {
        'predicted_dev_index_2w': round(float(predictions[0]), 2),
        'predicted_dev_index_4w': round(float(predictions[1]), 2),
        'trend': trend,
        'confidence': float(model.score(weeks, dev_indices))
    }


def benchmark_against_cohort(
        patient_features: Dict[str, float], cohort_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compare patient against gestational-age matched cohort."""
    cohort_indices = [d.get('developmental_index', 0) for d in cohort_data]
    if not cohort_indices:
        return {
            'message': 'No cohort data available',
            'patient_percentile': None,
            'cohort_mean': None,
            'cohort_std': None
        }

    matched = [d for d in cohort_data if d.get(
        'gestational_weeks') == patient_features.get('gestational_weeks')]
    cohort = matched if matched else cohort_data
    cohort_values = np.array([d.get('developmental_index', 0) for d in cohort])
    patient_index = float(patient_features.get('developmental_index', 0))

    percentile = float(
        np.sum(
            cohort_values < patient_index) /
        len(cohort_values) *
        100)
    return {
        'patient_percentile': round(percentile, 2),
        'cohort_mean': float(np.mean(cohort_values)),
        'cohort_std': float(np.std(cohort_values)),
        'matched_cohort_size': len(cohort)
    }
