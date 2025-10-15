---
applyTo:
  - "main.py"
  - "**/feedback_loop*.py"
  - "**/test_feedback_loop*.py"
---

# Machine Learning Code Instructions

## ML Model Development

### Model Architecture
- LSTM models: Use for sequential/time-series prediction
- XGBoost: Use for classification (buy/sell/hold signals)
- Logistic Regression: Use as baseline model
- Ensemble: Combine predictions from multiple models

### Data Preparation
- Normalize/standardize features before training
- Use proper train/validation/test splits (e.g., 70/15/15)
- Handle missing values appropriately
- Create temporal features (lag, rolling windows)
- Avoid look-ahead bias in feature engineering

### Model Training
- Use early stopping to prevent overfitting
- Track training metrics (accuracy, loss, precision, recall)
- Save model weights after training to avoid retraining
- Implement graceful handling when models aren't trained yet
- Log training progress for debugging

### Feedback Loop System
- Three-tier training schedule:
  - Tier 1 (Basic): Every 1 hour, trains Logistic Regression
  - Tier 2 (Intermediate): Every 6 hours, trains LR + XGBoost  
  - Tier 3 (Advanced): Every 24 hours, trains all models including LSTM
- Log all predictions with timestamps
- Track prediction accuracy vs actual outcomes
- Trigger retraining when accuracy drops below threshold (default: 55%)
- Use rolling window of recent predictions for evaluation

### Model Persistence
- Save models to `model_weights/` directory (gitignored)
- Use descriptive filenames with timestamps
- Implement versioning for model tracking
- Support loading models from previous sessions

### Performance Metrics
- Primary metric: Prediction accuracy
- Track precision, recall, F1-score for classification
- Monitor prediction latency
- Log confusion matrices for debugging

### Error Handling
- Gracefully handle insufficient training data
- Fall back to simpler models if complex models fail
- Provide informative error messages for users
- Never crash the application due to ML errors

## Best Practices

### Risk Disclaimers
- Always include disclaimers that predictions are not guaranteed
- Emphasize educational purpose only
- Warn about cryptocurrency trading risks
- Never make promises about returns or accuracy

### Resource Management
- Use batch prediction when possible
- Avoid retraining during prediction
- Cache predictions when appropriate
- Use background threads for long-running training
