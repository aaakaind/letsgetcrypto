# Feedback Loop: Automated Training and Continuous Learning

## Overview

The LetsGetCrypto application now includes an advanced **Feedback Loop** system that enables automated, continuous model training and improvement. This system implements a tiered training architecture with intelligent retraining triggers based on both time intervals and performance degradation.

## Key Features

### 🎯 Tiered Training System

The feedback loop implements three tiers of training with increasing complexity and computational requirements:

| Tier | Name | Interval | Models Trained | Purpose |
|------|------|----------|----------------|---------|
| **Tier 1** | Basic | 1 hour | Logistic Regression | Fast, frequent updates with lightweight model |
| **Tier 2** | Intermediate | 6 hours | Logistic Regression + XGBoost | Balanced performance and speed |
| **Tier 3** | Advanced | 24 hours | All models (LR + XGBoost + LSTM) | Complete retraining with deep learning |

### 📊 Performance Tracking

- **Historical Metrics**: Tracks accuracy and other metrics for all trained models over time
- **Trend Analysis**: Automatically detects if model performance is improving, degrading, or stable
- **Performance History**: Maintains a log of all training sessions with timestamps and metrics
- **Model Versioning**: Supports tracking different versions of trained models

### 🔄 Intelligent Retraining Triggers

The system automatically decides when to retrain models based on:

1. **Time-Based Triggers**: Each tier has a specified interval
   - Tier 1: Retrains every hour for up-to-date predictions
   - Tier 2: Retrains every 6 hours for better model quality
   - Tier 3: Retrains daily for comprehensive deep learning updates

2. **Performance-Based Triggers**: Retrains when accuracy drops below threshold
   - Default threshold: 55% accuracy
   - Evaluation window: Last 10 predictions
   - Prevents continued use of degraded models

### 📝 Prediction Logging

- Logs all predictions along with actual market outcomes
- Tracks prediction accuracy over time
- Uses recent predictions to evaluate model performance
- Supports continuous learning from real-world results
- Maintains a rolling window of 1000 most recent predictions

## Configuration

The feedback loop can be configured through the `FeedbackLoop.config` dictionary:

```python
config = {
    'tier1_interval': 3600,           # Tier 1: retrain every hour (seconds)
    'tier2_interval': 21600,          # Tier 2: retrain every 6 hours
    'tier3_interval': 86400,          # Tier 3: retrain daily
    'performance_threshold': 0.55,    # Minimum acceptable accuracy (55%)
    'improvement_threshold': 0.02,    # Minimum improvement to consider (2%)
    'evaluation_window': 10,          # Number of predictions to evaluate
}
```

### Customizing Configuration

You can modify these values to suit your needs:

- **Shorter intervals**: More frequent retraining, higher computational cost
- **Longer intervals**: Less frequent retraining, lower cost, potentially outdated models
- **Higher threshold**: More aggressive retraining, better model quality
- **Lower threshold**: More tolerant of performance dips, less retraining

## Usage

### GUI Application

#### Enable Automatic Feedback Loop

1. Launch the application: `python main.py`
2. In the "Feedback Loop (Auto-Learning)" section:
   - Check "Enable Automatic Feedback Loop"
   - The system will now automatically check for retraining needs every hour

#### Manual Training Cycle

1. Click "Run Training Cycle" to manually trigger a feedback loop cycle
2. The system will:
   - Fetch fresh market data
   - Check which tiers need retraining
   - Execute training for eligible tiers
   - Update performance metrics
   - Log results

#### View Feedback Loop Status

1. Click "Show Feedback Status" to view:
   - Current training status
   - Recent prediction performance
   - Last training times for each tier
   - Performance trends for each model
   - Configuration settings

### Programmatic Usage

```python
from main import MLModels, FeedbackLoop, DataFetcher

# Initialize components
ml_models = MLModels()
data_fetcher = DataFetcher()
feedback_loop = FeedbackLoop(ml_models, data_fetcher)

# Execute a training cycle
result = feedback_loop.execute_training_cycle(
    symbol='bitcoin',
    days=30
)

# Log prediction outcomes for learning
prediction = {'signal': 'BUY', 'ensemble': 0.7}
actual_outcome = 'BUY'  # or 'SELL' or 'HOLD'
feedback_loop.log_prediction_outcome(prediction, actual_outcome)

# Check performance
performance = feedback_loop.calculate_recent_performance()
print(f"Recent accuracy: {performance['accuracy']:.2%}")

# Get status
status = feedback_loop.get_feedback_loop_status()
print(f"Training in progress: {status['training_in_progress']}")
```

## Architecture

### Class Structure

```
FeedbackLoop
├── __init__(ml_models, data_fetcher)
├── Config Management
│   └── config: dict
├── Training Methods
│   ├── tier1_training()
│   ├── tier2_training()
│   ├── tier3_training()
│   └── execute_training_cycle()
├── Performance Tracking
│   ├── log_prediction_outcome()
│   ├── calculate_recent_performance()
│   └── should_retrain()
└── Status Reporting
    └── get_feedback_loop_status()

MLModels (Enhanced)
├── Existing ML functionality
├── performance_history: list
├── model_versions: dict
├── save_performance_metrics()
└── get_performance_trend()
```

### Data Flow

```
1. User/Timer triggers training cycle
   ↓
2. FeedbackLoop.execute_training_cycle()
   ├── Fetches fresh data
   ├── Checks if each tier needs retraining
   └── Executes eligible tier training
   ↓
3. Tier training methods
   ├── Prepare features
   ├── Train models
   ├── Evaluate performance
   └── Save metrics
   ↓
4. MLModels.save_performance_metrics()
   └── Updates performance_history
   ↓
5. Results returned to caller
```

## Performance Considerations

### Computational Cost

- **Tier 1** (Logistic Regression): ~1-5 seconds
- **Tier 2** (LR + XGBoost): ~5-30 seconds
- **Tier 3** (All models + LSTM): ~30-300 seconds (depending on GPU availability)

### Memory Usage

- Prediction log: Limited to 1000 most recent entries
- Performance history: Grows with each training session (consider periodic cleanup)
- Trained models: Stored in memory (old versions not automatically deleted)

### Best Practices

1. **Enable GPU**: Significantly speeds up LSTM training in Tier 3
2. **Monitor logs**: Check for training errors or performance issues
3. **Adjust intervals**: Tune based on your computational resources
4. **Review trends**: Regularly check model performance trends
5. **Balance tiers**: Use Tier 1 for quick updates, Tier 3 for deep learning

## Monitoring and Logging

The feedback loop uses the `loguru` logger for comprehensive logging:

- **Info**: Training start/completion, status updates
- **Success**: Successful training with accuracy metrics
- **Warning**: Skipped training, insufficient data
- **Error**: Training failures, data fetch errors

### Log Examples

```
[INFO] Starting Tier 1 (Basic) training...
[SUCCESS] Tier 1 training complete: accuracy=0.6234
[INFO] Starting training cycle for bitcoin
[SUCCESS] Training cycle complete: 2 tier(s) trained
[WARNING] Training already in progress, skipping cycle
[ERROR] Error in Tier 2 training: Insufficient data
```

## Integration with Existing Features

### With ML Models

- All trained models are stored in `MLModels.models` dictionary
- Scalers are maintained in `MLModels.scalers` dictionary
- Performance history is tracked in `MLModels.performance_history`
- Predictions use the most recently trained models

### With Trading Engine

- Trading signals benefit from continuously improved models
- Prediction accuracy directly impacts trade success
- Performance metrics can inform risk management decisions

### With GUI

- Feedback loop status visible in dedicated tab
- Manual controls for immediate training cycles
- Automatic mode runs in background via timer
- Real-time logging in status panel

## Troubleshooting

### Training Not Triggering

**Issue**: Automatic training doesn't start

**Solutions**:
- Ensure "Enable Automatic Feedback Loop" is checked
- Check that sufficient time has passed since last training
- Verify data fetching is working properly
- Review logs for error messages

### Poor Performance

**Issue**: Models not improving despite retraining

**Solutions**:
- Increase training data window (more days)
- Adjust feature engineering
- Review prediction logging - ensure outcomes are accurate
- Consider external factors (market conditions)

### High Resource Usage

**Issue**: Application consuming too much CPU/memory

**Solutions**:
- Increase training intervals (reduce frequency)
- Disable Tier 3 if LSTM is too resource-intensive
- Reduce data window size
- Ensure old model versions are cleaned up

### Training Failures

**Issue**: Training cycles fail with errors

**Solutions**:
- Check data availability
- Verify all required libraries are installed
- Review feature preparation logs
- Ensure sufficient data for training (minimum 30-50 samples)

## Future Enhancements

Planned improvements for the feedback loop system:

1. **Adaptive Intervals**: Automatically adjust training frequency based on market volatility
2. **Multi-Asset Learning**: Learn from multiple cryptocurrencies simultaneously
3. **Transfer Learning**: Apply knowledge from one asset to another
4. **Hyperparameter Tuning**: Automatically optimize model parameters
5. **A/B Testing**: Compare different model configurations
6. **Ensemble Weighting**: Dynamic adjustment of model weights based on recent performance
7. **Cloud Training**: Offload heavy training to cloud resources
8. **Model Persistence**: Save and load trained models from disk

## Contributing

To extend the feedback loop functionality:

1. Add new training tiers in `FeedbackLoop` class
2. Implement new performance metrics in `MLModels`
3. Create custom retraining triggers
4. Add visualization for performance trends
5. Integrate with external monitoring systems

## References

- Main implementation: `main.py` (lines 338-1003)
- Test suite: `test_feedback_loop.py`
- Validation: `test_feedback_loop_simple.py`

## License

This feedback loop system is part of the LetsGetCrypto project and follows the same license terms as the main project.

---

**Note**: This system is designed for educational and research purposes. Always validate model predictions with your own analysis before making trading decisions.
