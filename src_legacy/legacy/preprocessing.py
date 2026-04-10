# General signal preprocessing — artifact removal, normalisation, rolling features

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler


class SignalPreprocessor:

    # Remove outliers beyond z-score threshold
    @staticmethod
    def remove_artifacts(data, threshold=3.0):
        z_scores = np.abs((data - data.mean()) / data.std())
        return data[z_scores < threshold]

    # Normalise with z-score or min-max
    @staticmethod
    def normalize_signal(data, method='zscore'):
        if method == 'zscore':
            scaler = StandardScaler()
        elif method == 'minmax':
            scaler = MinMaxScaler()
        else:
            raise ValueError("Method must be 'zscore' or 'minmax'")
        return pd.Series(
            scaler.fit_transform(data.values.reshape(-1, 1)).flatten(),
            index=data.index
        )

    # Rolling mean / std / min / max over a sliding window
    @staticmethod
    def compute_rolling_features(data, window=5):
        features = pd.DataFrame(index=data.index)
        features['rolling_mean'] = data.rolling(window=window).mean()
        features['rolling_std'] = data.rolling(window=window).std()
        features['rolling_min'] = data.rolling(window=window).min()
        features['rolling_max'] = data.rolling(window=window).max()
        return features.dropna()


class DataCleaner:

    # Forward-fill then back-fill, or linear interpolation
    @staticmethod
    def handle_missing_values(data, method='ffill'):
        if method == 'ffill':
            return data.fillna(method='ffill').fillna(method='bfill')
        elif method == 'interpolate':
            return data.interpolate(method='linear')
        else:
            raise ValueError("Method must be 'ffill' or 'interpolate'")

    # Keep only rows present in both DataFrames
    @staticmethod
    def align_datasets(df1, df2):
        common_index = df1.index.intersection(df2.index)
        return df1.loc[common_index], df2.loc[common_index]
