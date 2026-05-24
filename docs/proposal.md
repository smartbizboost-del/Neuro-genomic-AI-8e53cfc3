# Neuro-Genomic AI: Adaptive HCI Research Project

## Project Overview

This research project integrates physiological signals, cognitive state analysis, and genomic insights to study and develop adaptive human-computer interaction (HCI) interfaces. The core objective is to create an AI-driven system that predicts user cognitive load and adapts interface complexity in real-time.

## Research Objectives

1. **Physiological Signal Analysis**: Collect and analyze heart rate, electrodermal activity, EEG, and respiration patterns
2. **Cognitive State Classification**: Build ML models to classify user cognitive states (focused, distracted, overloaded)
3. **Behavioral Pattern Recognition**: Analyze user interaction patterns (mouse movement, typing speed, task completion time)
4. **Genomic Exploration**: Investigate potential biological predispositions affecting cognitive load (optional research extension)
5. **Adaptive Interface Design**: Develop algorithms that suggest interface modifications based on real-time cognitive state

## Data Sources

### Physiological Signals
- **PhysioNet**: Open-access physiological datasets
- **OpenBCI**: Public EEG and biosignal datasets
- **MIT Stress Recognition Dataset**: Multi-modal physiological signals

Signals collected:
- Heart Rate Variability (HRV)
- Electrodermal Activity (EDA)
- EEG Power Spectral Density
- Respiration Rate

### Behavioral Interaction Data
- Mouse movement patterns
- Typing speed and rhythm
- Click frequency and timing
- Task completion time
- User attention indicators

### Genomic Data (Optional)
- **NCBI Gene Expression Omnibus (GEO)**: Gene expression profiles
- **1000 Genomes Project**: Population genomic variation
- **GTEx**: Tissue-specific gene expression

## System Architecture

```
Data Sources
    ↓
Data Collection & Aggregation
    ↓
Preprocessing & Normalization
    ↓
Feature Extraction & Engineering
    ↓
Machine Learning Models
    ↓
Cognitive State Classification
    ↓
Adaptation Recommendation Engine
    ↓
Adaptive HCI Interface
```

## Key Deliverables

1. **Data Pipeline**: Unified system for loading and processing multi-modal data
2. **Preprocessing Modules**: Signal normalization, artifact removal, feature engineering
3. **ML Models**: Random Forest and Gradient Boosting classifiers for cognitive state prediction
4. **Visualization Suite**: Exploratory data analysis and results visualization
5. **Research Notebooks**: Detailed analysis and findings documentation

## Expected Outcomes

- Demonstrate correlation between physiological signals and cognitive load
- Develop a predictive model with >85% accuracy for cognitive state classification
- Propose novel interface adaptations based on user state
- Create a reusable framework for physiological computing research

## References

- Fairclough, S. H. (2009). Fundamentals of physiological computing. *Interacting with Computers*, 21(1-2), 133-145.
- Zijlstra, F. R. H., & Roe, R. A. (1999). An introduction to research on stress and health. In *Handbook of Work and Organizational Psychology*
- Norman, D. A., & Draper, S. W. (1986). User centered system design: New perspectives on human-computer interaction.

## Timeline

- **Phase 1** (Week 1-2): Data collection and exploration
- **Phase 2** (Week 3-4): Preprocessing and feature engineering
- **Phase 3** (Week 5-6): Model development and validation
- **Phase 4** (Week 7-8): System integration and documentation

## Authors & Acknowledgments

*To be updated*

---

**Last Updated**: March 2026
