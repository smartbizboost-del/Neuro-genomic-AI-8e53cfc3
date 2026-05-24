"""Unsupervised clustering helpers (05_unsupervised_clustering.ipynb)
Provides a minimal clustering wrapper using scikit-learn KMeans for example purposes.
"""
import numpy as np
from sklearn.cluster import KMeans


def cluster_features(X: np.ndarray, n_clusters: int = 3) -> dict:
    if X is None or len(X) == 0:
        return {'clusters': [], 'labels': []}
    k = min(n_clusters, len(X))
    km = KMeans(n_clusters=k, random_state=42)
    labels = km.fit_predict(X)
    return {'labels': labels.tolist(), 'centroids': km.cluster_centers_.tolist()}


def run(X, n_clusters=3):
    return cluster_features(X, n_clusters)
