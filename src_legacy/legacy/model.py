# ML Models — cognitive state classification and interface adaptation

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd


class CognitiveStateClassifier:

    # model_type: 'rf' (Random Forest) or 'gb' (Gradient Boosting)
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

    # Returns accuracy + weighted F1
    def evaluate(self, X_test, y_test):
        preds = self.predict(X_test)
        return {
            'accuracy': accuracy_score(y_test, preds),
            'f1_score': f1_score(y_test, preds, average='weighted'),
        }

    # Feature importance sorted descending
    def get_feature_importance(self, feature_names):
        return pd.DataFrame({
            'feature': feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)


class AdaptivityPredictor:

    def __init__(self):
        self.classifier = CognitiveStateClassifier(model_type='rf')

    # Train on 80/20 split, return eval metrics
    def fit(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        self.classifier.train(X_train, y_train)
        return self.classifier.evaluate(X_test, y_test)

    # Rule-based adaptation suggestion
    def suggest_adaptation(self, user_state):
        if user_state.get('cognitive_load', 0) > 0.7:
            return 'REDUCE_COMPLEXITY'
        elif user_state.get('engagement', 0) < 0.3:
            return 'INCREASE_INTERACTIVITY'
        else:
            return 'MAINTAIN_CURRENT'


# Compare RF, Gradient Boosting, and Neural Network on same split
def evaluate_candidate_models(X, y, test_size=0.2, random_state=42):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    candidates = {
        'RandomForest': CognitiveStateClassifier('rf'),
        'GradientBoosting': CognitiveStateClassifier('gb'),
        'NeuralNetwork': CognitiveStateClassifier('nn'),
    }

    rows = []
    best_name = None
    best_f1 = -1.0

    for name, clf in candidates.items():
        clf.train(X_train, y_train)
        preds = clf.predict(X_test)
        acc = accuracy_score(y_test, preds)
        f1 = f1_score(y_test, preds, average='weighted')
        rows.append({'model': name, 'accuracy': float(acc), 'f1_weighted': float(f1)})
        if f1 > best_f1:
            best_f1 = f1
            best_name = name

    leaderboard = pd.DataFrame(rows).sort_values('f1_weighted', ascending=False).reset_index(drop=True)
    return {
        'leaderboard': leaderboard,
        'best_model_name': best_name,
        'best_f1_weighted': float(best_f1),
        'models': candidates,
    }
