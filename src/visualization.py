"""Notebook-friendly visualization helpers with optional seaborn support."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd


class SignalVisualizer:
    @staticmethod
    def plot_signal(data, title: str = "Signal", ylabel: str = "Amplitude"):
        fig = plt.figure(figsize=(12, 4))
        plt.plot(data.values, linewidth=0.8)
        plt.title(title, fontsize=14, fontweight="bold")
        plt.ylabel(ylabel)
        plt.xlabel("Time")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        return fig

    @staticmethod
    def plot_multiple_signals(data, title: str = "Signals"):
        n = len(data.columns)
        fig, axes = plt.subplots(n, 1, figsize=(12, 3 * n))
        if n == 1:
            axes = [axes]
        for idx, col in enumerate(data.columns):
            axes[idx].plot(data[col].values, linewidth=0.8)
            axes[idx].set_title(col, fontweight="bold")
            axes[idx].set_ylabel("Amplitude")
            axes[idx].grid(True, alpha=0.3)
        plt.suptitle(title, fontsize=14, fontweight="bold", y=1.001)
        plt.tight_layout()
        return fig

    @staticmethod
    def plot_signal_distribution(data, title: str = "Distribution"):
        fig, axes = plt.subplots(1, 2, figsize=(12, 4))
        axes[0].hist(data.values, bins=30, alpha=0.7, edgecolor="black")
        axes[0].set_title(f"{title} - Histogram", fontweight="bold")
        axes[0].set_xlabel("Value")
        axes[0].set_ylabel("Frequency")
        axes[0].grid(True, alpha=0.3)
        try:
            import seaborn as sns  # type: ignore

            sns.kdeplot(data=data, ax=axes[1], fill=True)
        except Exception:
            axes[1].hist(
                data.values,
                bins=30,
                density=True,
                alpha=0.7,
                edgecolor="black")
        axes[1].set_title(f"{title} - Distribution", fontweight="bold")
        axes[1].set_xlabel("Value")
        axes[1].grid(True, alpha=0.3)
        plt.tight_layout()
        return fig


class AnalysisVisualizer:
    @staticmethod
    def plot_feature_importance(importance_df, top_n: int = 15):
        top = importance_df.head(top_n)
        fig = plt.figure(figsize=(10, 6))
        try:
            import seaborn as sns  # type: ignore

            sns.barplot(
                data=top,
                y="feature",
                x="importance",
                palette="viridis")
        except Exception:
            plt.barh(top["feature"], top["importance"])
        plt.title(
            f"Top {top_n} Feature Importance",
            fontsize=14,
            fontweight="bold")
        plt.xlabel("Importance Score")
        plt.tight_layout()
        return fig

    @staticmethod
    def plot_correlation_matrix(data, figsize=(10, 8)):
        fig = plt.figure(figsize=figsize)
        corr = pd.DataFrame(data).corr()
        try:
            import seaborn as sns  # type: ignore

            sns.heatmap(
                corr,
                annot=True,
                fmt=".2f",
                cmap="coolwarm",
                center=0,
                square=True,
                cbar_kws={
                    "label": "Correlation"})
        except Exception:
            plt.imshow(corr, cmap="coolwarm", aspect="auto", vmin=-1, vmax=1)
            plt.colorbar(label="Correlation")
            plt.xticks(range(len(corr.columns)),
                       corr.columns, rotation=45, ha="right")
            plt.yticks(range(len(corr.index)), corr.index)
        plt.title("Feature Correlation Matrix", fontsize=14, fontweight="bold")
        plt.tight_layout()
        return fig


__all__ = ["AnalysisVisualizer", "SignalVisualizer"]
