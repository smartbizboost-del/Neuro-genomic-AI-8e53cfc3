# Maturation Scoring — gestational age regression or preterm/term/post-term classification

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score, accuracy_score, f1_score


class MaturationScorer:

    MATURITY_CLASSES = ['preterm', 'term', 'post-term']

    # mode: 'regression' (gestational age) or 'classification' (maturity category)
    def __init__(self, mode='regression'):
        if mode not in ('regression', 'classification'):
            raise ValueError("mode must be 'regression' or 'classification'")

        self.mode = mode
        self.scaler = StandardScaler()
        self.feature_names_ = None
        self.is_fitted_ = False

        if mode == 'regression':
            self.model = GradientBoostingRegressor(
                n_estimators=200, max_depth=4, learning_rate=0.05, random_state=42
            )
        else:
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)

    # Fit on 80/20 split, return eval metrics
    def fit(self, X, y):
        self.feature_names_ = list(X.columns)
        X_scaled = self.scaler.fit_transform(X)
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        self.model.fit(X_train, y_train)
        self.is_fitted_ = True
        return self._evaluate(X_test, y_test)

    def predict(self, X):
        self._check_fitted()
        return self.model.predict(self.scaler.transform(X))

    # Classification mode only
    def predict_proba(self, X):
        if self.mode != 'classification':
            raise ValueError("predict_proba() is only available in classification mode.")
        self._check_fitted()
        return self.model.predict_proba(self.scaler.transform(X))

    # Feature importance sorted descending
    def get_feature_importance(self):
        self._check_fitted()
        return pd.DataFrame({
            'feature': self.feature_names_,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False).reset_index(drop=True)

    # Map gestational age → preterm (<37 wk) / term (37–41) / post-term (>41)
    @staticmethod
    def maturation_category(gestational_age_weeks):
        if gestational_age_weeks < 37:
            return 'preterm'
        elif gestational_age_weeks <= 41:
            return 'term'
        else:
            return 'post-term'

    # Rule-based maturation index [0,1] from HRV features
    @staticmethod
    def hrv_maturation_heuristic(hrv_features):
        score = 0.0
        factors = 0

        # Fetal HR in normal range 120–160 bpm
        hr = hrv_features.get('heart_rate_mean', np.nan)
        if not np.isnan(hr):
            score += float(120 <= hr <= 160)
            factors += 1

        # RMSSD increases with maturity (range ~10–40 ms)
        rmssd = hrv_features.get('rmssd', np.nan)
        if not np.isnan(rmssd):
            score += float(np.clip((rmssd - 5) / 35, 0, 1))
            factors += 1

        # pNN50 increases with parasympathetic maturity
        pnn50 = hrv_features.get('pnn50', np.nan)
        if not np.isnan(pnn50):
            score += float(np.clip(pnn50 / 20, 0, 1))
            factors += 1

        return score / factors if factors > 0 else np.nan

    def _check_fitted(self):
        if not self.is_fitted_:
            raise RuntimeError("Model is not fitted yet. Call fit() first.")

    def _evaluate(self, X_test, y_test):
        preds = self.model.predict(X_test)
        if self.mode == 'regression':
            return {
                'mae_weeks': float(mean_absolute_error(y_test, preds)),
                'r2': float(r2_score(y_test, preds))
            }
        else:
            return {
                'accuracy': float(accuracy_score(y_test, preds)),
                'f1_weighted': float(f1_score(y_test, preds, average='weighted'))
            }


# ── Maturation Index ────────────────────────────────────────────────────────────
# Research-grade 0–1 index with bootstrap confidence interval.
# NOT a clinical diagnostic tool — for research and exploratory use only.

class MaturationIndex:
    """
    Compute a normalized fetal maturation index [0, 1] from HRV features.

    The index fuses three HRV proxies of autonomic maturity:
      - Fetal heart rate in the expected 120–160 bpm range
      - RMSSD (short-term RR variability, normalised to 5–40 ms range)
      - pNN50 (parasympathetic activity, normalised to 0–20 %)

    A bootstrap procedure over the feature vector with jitter noise yields
    a 95 % confidence interval that reflects measurement uncertainty.

    DISCLAIMER: This index is a research prototype.  It must not be used for
    clinical diagnosis, screening, or any medical decision-making.
    """

    DISCLAIMER = (
        "RESEARCH PROTOTYPE — NOT FOR CLINICAL USE. "
        "This maturation index is an exploratory research tool. "
        "It has not been validated for clinical diagnosis or medical decisions."
    )

    def __init__(self, n_bootstrap: int = 1000, noise_std: float = 0.03, seed: int = 42):
        self.n_bootstrap = n_bootstrap
        self.noise_std = noise_std
        self.rng = np.random.default_rng(seed)

    def compute(self, hrv_features: dict) -> dict:
        """
        Parameters
        ----------
        hrv_features : dict
            Keys expected: 'heart_rate_mean', 'rmssd', 'pnn50'.
            Missing / NaN keys are handled gracefully.

        Returns
        -------
        dict with keys:
            score       – point estimate [0, 1]
            ci_lower    – 2.5th percentile of bootstrap distribution
            ci_upper    – 97.5th percentile of bootstrap distribution
            ci_width    – ci_upper - ci_lower (proxy for uncertainty)
            n_features  – number of non-NaN features used
            disclaimer  – mandatory research disclaimer string
        """
        point = self._score(hrv_features)
        bootstrap_scores = self._bootstrap(hrv_features)

        ci_lower = float(np.nanpercentile(bootstrap_scores, 2.5))
        ci_upper = float(np.nanpercentile(bootstrap_scores, 97.5))

        return {
            'score': float(point) if not np.isnan(point) else None,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'ci_width': ci_upper - ci_lower,
            'n_features': self._count_valid(hrv_features),
            'disclaimer': self.DISCLAIMER,
        }

    # ── private helpers ──────────────────────────────────────────────────────

    def _score(self, features: dict) -> float:
        """Weighted fusion of normalised HRV sub-scores → [0, 1]."""
        components = []
        weights = []

        hr = features.get('heart_rate_mean', np.nan)
        if not np.isnan(float(hr if hr is not None else np.nan)):
            # Binary: 1 if in expected fetal HR window, else 0
            components.append(float(120 <= hr <= 160))
            weights.append(1.0)

        rmssd = features.get('rmssd', np.nan)
        if not np.isnan(float(rmssd if rmssd is not None else np.nan)):
            # Linearly normalise 5–40 ms → 0–1, clipped
            components.append(float(np.clip((rmssd - 5.0) / 35.0, 0.0, 1.0)))
            weights.append(1.5)  # higher weight: strong maturity marker

        pnn50 = features.get('pnn50', np.nan)
        if not np.isnan(float(pnn50 if pnn50 is not None else np.nan)):
            # Normalise 0–20 % → 0–1, clipped
            components.append(float(np.clip(pnn50 / 20.0, 0.0, 1.0)))
            weights.append(1.0)

        if not components:
            return np.nan

        return float(np.average(components, weights=weights))

    def _bootstrap(self, features: dict) -> np.ndarray:
        """Add Gaussian jitter to numeric features and re-score n_bootstrap times."""
        scores = np.empty(self.n_bootstrap)
        keys = ['heart_rate_mean', 'rmssd', 'pnn50']
        base_values = np.array([float(features.get(k, np.nan) or np.nan) for k in keys])
        valid_mask = ~np.isnan(base_values)

        for i in range(self.n_bootstrap):
            jittered = base_values.copy()
            jittered[valid_mask] += self.rng.normal(0, self.noise_std * np.abs(base_values[valid_mask]) + 1e-6)
            jittered_features = {k: jittered[j] for j, k in enumerate(keys)}
            scores[i] = self._score(jittered_features)

        return scores

    def _count_valid(self, features: dict) -> int:
        keys = ['heart_rate_mean', 'rmssd', 'pnn50']
        return sum(
            1 for k in keys
            if features.get(k) is not None and not np.isnan(float(features.get(k)))
        )


def compute_maturation_index(hrv_features: dict, n_bootstrap: int = 1000) -> dict:
    """Convenience wrapper around MaturationIndex.compute()."""
    return MaturationIndex(n_bootstrap=n_bootstrap).compute(hrv_features)
