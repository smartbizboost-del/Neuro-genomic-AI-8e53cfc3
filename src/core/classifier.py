"""
ML Models — cognitive state classification and interface adaptation
Migrated from legacy architecture
"""
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd

class CognitiveStateClassifier:
    def __init__(self, model_type='rf'):
        if model_type == 'rf':
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        elif model_type == 'gb':
            self.model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        elif model_type == 'nn':
            self.model = Pipeline([
                ('scaler', StandardScaler()),
                ('mlp', MLPClassifier(
                    hidden_layer_sizes=(64, 32),
                    activation='relu',
                    solver='adam',
                    max_iter=600,
                    random_state=42
                ))
            ])
        else:
            raise ValueError("Model type must be 'rf', 'gb', or 'nn'")

    def train(self, X_train, y_train):
        self.model.fit(X_train, y_train)

    def predict(self, X):
        return self.model.predict(X)

    def evaluate(self, X_test, y_test):
        preds = self.predict(X_test)
        return {
            'accuracy': accuracy_score(y_test, preds),
            'f1_score': f1_score(y_test, preds, average='weighted'),
        }

    def get_feature_importance(self, feature_names):
        if hasattr(self.model, 'feature_importances_'):
            return pd.DataFrame({
                'feature': feature_names,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
        return pd.DataFrame()
