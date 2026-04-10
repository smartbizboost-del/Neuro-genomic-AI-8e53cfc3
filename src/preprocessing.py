"""Compatibility layer for preprocessing helpers used by notebooks."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler

from src.core.ecg_unsupervised.preprocessing import ECGPreprocessor


class SignalPreprocessor:
	"""Legacy signal preprocessing helpers."""

	@staticmethod
	def remove_artifacts(data, threshold: float = 3.0):
		z_scores = np.abs((data - data.mean()) / data.std())
		return data[z_scores < threshold]

	@staticmethod
	def normalize_signal(data, method: str = "zscore"):
		if method == "zscore":
			scaler = StandardScaler()
		elif method == "minmax":
			scaler = MinMaxScaler()
		else:
			raise ValueError("Method must be 'zscore' or 'minmax'")
		return pd.Series(scaler.fit_transform(data.values.reshape(-1, 1)).flatten(), index=data.index)

	@staticmethod
	def compute_rolling_features(data, window: int = 5):
		features = pd.DataFrame(index=data.index)
		features["rolling_mean"] = data.rolling(window=window).mean()
		features["rolling_std"] = data.rolling(window=window).std()
		features["rolling_min"] = data.rolling(window=window).min()
		features["rolling_max"] = data.rolling(window=window).max()
		return features.dropna()


class DataCleaner:
	"""Legacy tabular data cleaning helpers."""

	@staticmethod
	def handle_missing_values(data, method: str = "ffill"):
		if method == "ffill":
			return data.fillna(method="ffill").fillna(method="bfill")
		if method == "interpolate":
			return data.interpolate(method="linear")
		raise ValueError("Method must be 'ffill' or 'interpolate'")

	@staticmethod
	def align_datasets(df1, df2):
		common_index = df1.index.intersection(df2.index)
		return df1.loc[common_index], df2.loc[common_index]


__all__ = ["DataCleaner", "ECGPreprocessor", "SignalPreprocessor"]