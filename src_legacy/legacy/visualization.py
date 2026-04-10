# Visualization — signal plots, distributions, feature importance, correlation heatmaps

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np


class SignalVisualizer:

    # Single time-series plot
    @staticmethod
    def plot_signal(data, title="Signal", ylabel="Amplitude"):
        plt.figure(figsize=(12, 4))
        plt.plot(data.values, linewidth=0.8)
        plt.title(title, fontsize=14, fontweight='bold')
        plt.ylabel(ylabel)
        plt.xlabel('Time')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        return plt.gcf()

    # One subplot per column
    @staticmethod
    def plot_multiple_signals(data, title="Signals"):
        n = len(data.columns)
        fig, axes = plt.subplots(n, 1, figsize=(12, 3 * n))
        if n == 1:
            axes = [axes]
        for idx, col in enumerate(data.columns):
            axes[idx].plot(data[col].values, linewidth=0.8)
            axes[idx].set_title(col, fontweight='bold')
            axes[idx].set_ylabel('Amplitude')
            axes[idx].grid(True, alpha=0.3)
        plt.suptitle(title, fontsize=14, fontweight='bold', y=1.001)
        plt.tight_layout()
        return fig

    # Histogram + KDE side by side
    @staticmethod
    def plot_signal_distribution(data, title="Distribution"):
        fig, axes = plt.subplots(1, 2, figsize=(12, 4))
        axes[0].hist(data.values, bins=30, alpha=0.7, edgecolor='black')
        axes[0].set_title(f'{title} - Histogram', fontweight='bold')
        axes[0].set_xlabel('Value')
        axes[0].set_ylabel('Frequency')
        axes[0].grid(True, alpha=0.3)
        sns.kdeplot(data=data, ax=axes[1], fill=True)
        axes[1].set_title(f'{title} - Distribution', fontweight='bold')
        axes[1].set_xlabel('Value')
        axes[1].grid(True, alpha=0.3)
        plt.tight_layout()
        return fig


class AnalysisVisualizer:

    # Horizontal bar chart of top-N feature importances
    @staticmethod
    def plot_feature_importance(importance_df, top_n=15):
        top = importance_df.head(top_n)
        plt.figure(figsize=(10, 6))
        sns.barplot(data=top, y='feature', x='importance', palette='viridis')
        plt.title(f'Top {top_n} Feature Importance', fontsize=14, fontweight='bold')
        plt.xlabel('Importance Score')
        plt.tight_layout()
        return plt.gcf()

    # Annotated correlation heatmap
    @staticmethod
    def plot_correlation_matrix(data, figsize=(10, 8)):
        plt.figure(figsize=figsize)
        corr = data.corr()
        sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm',
                    center=0, square=True, cbar_kws={'label': 'Correlation'})
        plt.title('Feature Correlation Matrix', fontsize=14, fontweight='bold')
        plt.tight_layout()
        return plt.gcf()
