# docs/risk_management.md

## Failure Mode 1: Poor Signal Quality
- **Detection**: SQA module flags POOR
- **Mitigation**: Reject analysis, prompt user to reposition electrodes
- **Residual risk**: Low

## Failure Mode 2: Maternal Cancellation Failure
- **Detection**: BiLSTM confidence low
- **Mitigation**: Fallback to ICA, then flag as ACCEPTABLE
- **Residual risk**: Medium – user warned

## Failure Mode 3: Model Overfitting
- **Detection**: Performance drop on external validation
- **Mitigation**: Regular retraining, external validation every 6 months
- **Residual risk**: Low – monitored