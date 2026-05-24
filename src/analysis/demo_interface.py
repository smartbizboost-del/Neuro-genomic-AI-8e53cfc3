"""Demo interface utilities (from 04_demo_interface.ipynb)
Provides a simple mock-runner to produce demo results for UI and testing.
"""
import numpy as np

def demo_result(seed: int = 42) -> dict:
    rng = np.random.default_rng(seed)
    return {
        'developmental_index': float(rng.uniform(0.6, 0.9)),
        'confidence_interval': (0.72, 0.81),
        'signal_quality': int(rng.integers(70, 98)),
        'risk_scores': {
            'IUGR': {'value': int(rng.integers(5, 20)), 'level': 'Low', 'ci': (5, 20)},
            'Preterm': {'value': int(rng.integers(10, 30)), 'level': 'Moderate', 'ci': (10, 30)},
            'Hypoxia': {'value': int(rng.integers(2, 12)), 'level': 'Low', 'ci': (2, 12)},
        },
    }


def run_demo():
    return demo_result()
