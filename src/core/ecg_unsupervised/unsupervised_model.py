from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN, KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import calinski_harabasz_score, silhouette_score
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler


class UnsupervisedFetalECGModel:
    def __init__(self, method: str = "gmm", n_clusters: int = 3,
                 random_state: int = 42):
        self.method = method
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=0.95, random_state=random_state)
        self.model = self._build_model()

    def _build_model(self):
        if self.method == "kmeans":
            return KMeans(n_clusters=self.n_clusters,
                          random_state=self.random_state, n_init=10)
        if self.method == "gmm":
            return GaussianMixture(
                n_components=self.n_clusters, random_state=self.random_state)
        if self.method == "dbscan":
            return DBSCAN(eps=0.8, min_samples=5)
        raise ValueError("method must be one of: kmeans, gmm, dbscan")

    def fit_predict(
            self, features: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
        x = self.scaler.fit_transform(features.values)
        x_pca = self.pca.fit_transform(x)
        if self.method == "gmm":
            labels = self.model.fit_predict(x_pca)
        else:
            labels = self.model.fit_predict(x_pca)
        return labels, x_pca

    @staticmethod
    def evaluate_clusters(
            x: np.ndarray, labels: np.ndarray) -> dict[str, float]:
        unique = np.unique(labels)
        n_clusters = len([u for u in unique if u >= 0])
        if n_clusters < 2:
            return {"num_clusters": float(
                n_clusters), "silhouette": np.nan, "calinski_harabasz": np.nan}
        return {
            "num_clusters": float(n_clusters),
            "silhouette": float(silhouette_score(x, labels)),
            "calinski_harabasz": float(calinski_harabasz_score(x, labels)),
        }
