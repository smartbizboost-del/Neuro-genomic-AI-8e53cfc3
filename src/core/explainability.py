# src/core/explainability.py
import shap
import numpy as np
import pandas as pd


class SHAPExplainer:
    def __init__(self, model, feature_names):
        self.model = model
        self.feature_names = feature_names
        self.explainer = shap.TreeExplainer(model)

    def explain_prediction(self, features):
        """Return SHAP values for a single prediction"""
        shap_values = self.explainer.shap_values(features)

        # Format for dashboard display
        explanations = []
        for i, (name, value) in enumerate(
                zip(self.feature_names, features[0])):
            explanations.append({
                'feature': name,
                'value': value,
                'impact': shap_values[0][i],
                'direction': 'increases risk' if shap_values[0][i] > 0 else 'decreases risk'
            })

        # Sort by absolute impact
        explanations.sort(key=lambda x: abs(x['impact']), reverse=True)
        return explanations

    def dashboard_format(self, explanations, top_n=3):
        """Format for dashboard display"""
        top_features = explanations[:top_n]
        text = "Why this risk score?\n"
        for feat in top_features:
            text += f"• {
                feat['feature']}: {
                feat['value']:.2f} → {
                feat['direction']}\n"
        return text
