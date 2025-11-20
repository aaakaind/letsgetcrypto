#!/bin/bash

# Machine Learning Environment Initialization Script
# This script initializes the ML environment and trains basic models

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🧠 Machine Learning Environment Initialization${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# Function to print step
print_step() {
    echo -e "\n${BLUE}▶ $1${NC}"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Step 1: Create directories
print_step "Creating ML directories..."
mkdir -p model_weights
mkdir -p data_cache
print_success "Directories created"

# Step 2: Create Python script for initial training
print_step "Creating initial ML training script..."

cat > /tmp/init_ml_models.py << 'PYEOF'
#!/usr/bin/env python3
"""
Initial ML Model Training Script
This script trains basic ML models with sample data
"""

import sys
import os
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("🔧 Initializing ML environment...")

# Check imports
try:
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    import xgboost as xgb
    print("✓ ML libraries loaded successfully")
except ImportError as e:
    print(f"✗ Error loading ML libraries: {e}")
    print("  Please run: pip install scikit-learn xgboost")
    sys.exit(1)

# Create model_weights directory if it doesn't exist
os.makedirs('model_weights', exist_ok=True)
os.makedirs('data_cache', exist_ok=True)

print("\n📊 Generating sample training data...")

# Generate synthetic cryptocurrency price data for training
def generate_sample_data(n_samples=1000):
    """Generate sample cryptocurrency data for initial model training"""
    np.random.seed(42)
    
    # Generate dates
    end_date = datetime.now()
    dates = [end_date - timedelta(days=n_samples-i) for i in range(n_samples)]
    
    # Generate price data with trend and noise
    base_price = 30000
    trend = np.linspace(0, 5000, n_samples)
    noise = np.random.normal(0, 1000, n_samples)
    prices = base_price + trend + noise
    prices = np.maximum(prices, 1000)  # Ensure positive prices
    
    # Generate features
    data = {
        'date': dates,
        'close': prices,
        'volume': np.random.uniform(1e9, 5e9, n_samples),
        'market_cap': prices * 19e6,  # Approximate BTC market cap
    }
    
    df = pd.DataFrame(data)
    
    # Add technical indicators
    df['returns'] = df['close'].pct_change()
    df['sma_7'] = df['close'].rolling(window=7).mean()
    df['sma_30'] = df['close'].rolling(window=30).mean()
    df['rsi'] = 50 + np.random.normal(0, 15, n_samples)  # Simplified RSI
    df['volatility'] = df['returns'].rolling(window=7).std()
    
    # Create target: 1 if price goes up tomorrow, 0 otherwise
    df['target'] = (df['close'].shift(-1) > df['close']).astype(int)
    
    # Drop NaN rows
    df = df.dropna()
    
    return df

# Generate data
print("  Generating 1000 samples of cryptocurrency data...")
df = generate_sample_data(1000)
print(f"✓ Generated {len(df)} samples")

# Save sample data
df.to_csv('data_cache/sample_training_data.csv', index=False)
print("✓ Sample data saved to data_cache/sample_training_data.csv")

print("\n🎯 Training Logistic Regression model...")

# Prepare features
feature_cols = ['returns', 'sma_7', 'sma_30', 'rsi', 'volatility', 'volume']
X = df[feature_cols].values
y = df['target'].values

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train Logistic Regression
lr_model = LogisticRegression(random_state=42, max_iter=1000)
lr_model.fit(X_train_scaled, y_train)

# Evaluate
train_score = lr_model.score(X_train_scaled, y_train)
test_score = lr_model.score(X_test_scaled, y_test)

print(f"  Training accuracy: {train_score:.2%}")
print(f"  Test accuracy: {test_score:.2%}")

# Save model
import pickle
with open('model_weights/logistic_regression.pkl', 'wb') as f:
    pickle.dump(lr_model, f)
with open('model_weights/scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)

print("✓ Logistic Regression model saved")

print("\n🚀 Training XGBoost model...")

# Train XGBoost
xgb_model = xgb.XGBClassifier(
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    random_state=42,
    eval_metric='logloss'
)
xgb_model.fit(X_train_scaled, y_train)

# Evaluate
train_score_xgb = xgb_model.score(X_train_scaled, y_train)
test_score_xgb = xgb_model.score(X_test_scaled, y_test)

print(f"  Training accuracy: {train_score_xgb:.2%}")
print(f"  Test accuracy: {test_score_xgb:.2%}")

# Save model
xgb_model.save_model('model_weights/xgboost_model.json')
print("✓ XGBoost model saved")

# Create model info file
model_info = {
    'created_at': datetime.now().isoformat(),
    'models': {
        'logistic_regression': {
            'file': 'logistic_regression.pkl',
            'train_accuracy': float(train_score),
            'test_accuracy': float(test_score),
            'features': feature_cols
        },
        'xgboost': {
            'file': 'xgboost_model.json',
            'train_accuracy': float(train_score_xgb),
            'test_accuracy': float(test_score_xgb),
            'features': feature_cols
        },
        'scaler': {
            'file': 'scaler.pkl'
        }
    },
    'data': {
        'samples': len(df),
        'train_samples': len(X_train),
        'test_samples': len(X_test),
        'features': feature_cols
    }
}

import json
with open('model_weights/model_info.json', 'w') as f:
    json.dump(model_info, f, indent=2)

print("✓ Model information saved")

print("\n" + "="*60)
print("✅ ML Environment Initialization Complete!")
print("="*60)
print("\nTrained Models:")
print(f"  • Logistic Regression (accuracy: {test_score:.2%})")
print(f"  • XGBoost (accuracy: {test_score_xgb:.2%})")
print("\nModel files saved in: model_weights/")
print("Sample data saved in: data_cache/")
print("\nNote: These are initial models trained on synthetic data.")
print("      Train with real cryptocurrency data for better predictions.")
print("="*60)
PYEOF

# Step 3: Run the training script
print_step "Training initial models..."
python /tmp/init_ml_models.py

if [ $? -eq 0 ]; then
    print_success "Initial models trained successfully"
else
    print_warning "Model training encountered issues"
fi

# Step 4: Create README for ML directory
print_step "Creating ML documentation..."

cat > model_weights/README.md << 'MDEOF'
# Model Weights Directory

This directory contains trained machine learning models for cryptocurrency prediction.

## Available Models

### 1. Logistic Regression (`logistic_regression.pkl`)
- **Type**: Binary classification (price up/down)
- **Features**: Returns, SMA 7/30, RSI, Volatility, Volume
- **Use**: Fast baseline predictions

### 2. XGBoost (`xgboost_model.json`)
- **Type**: Gradient boosting classifier
- **Features**: Same as Logistic Regression
- **Use**: More accurate predictions

### 3. Standard Scaler (`scaler.pkl`)
- **Type**: Feature normalization
- **Use**: Preprocessing for both models

## Model Information

See `model_info.json` for detailed information about:
- Training accuracy
- Test accuracy
- Feature list
- Training date
- Dataset statistics

## Retraining Models

Models can be retrained through:
1. **Desktop GUI**: Click "Train Models" button
2. **Web Dashboard**: Use the training interface
3. **Feedback Loop**: Automatic retraining based on performance
4. **Manual Script**: Run `./init_ml_environment.sh` or `bash init_ml_environment.sh`

## Model Files

All model files are gitignored for security and size reasons.
Each deployment should train its own models based on current data.

## Notes

- Initial models use synthetic data for demonstration
- Train with real cryptocurrency data for production use
- Models are automatically versioned with timestamps
- Feedback loop system continuously improves models

For more information, see:
- `FEEDBACK_LOOP.md` - Automated training system
- `README_APP.md` - Full application guide
- Main `README.md` - Project overview
MDEOF

print_success "ML documentation created"

# Final summary
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ ML Environment Ready!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}What's been set up:${NC}"
echo -e "  ✓ Model directories created"
echo -e "  ✓ Initial models trained (Logistic Regression, XGBoost)"
echo -e "  ✓ Sample training data generated"
echo -e "  ✓ Feature scaler configured"
echo -e "  ✓ Documentation added"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo -e "  1. Start the application (web or desktop)"
echo -e "  2. Select a cryptocurrency"
echo -e "  3. Fetch real market data"
echo -e "  4. Retrain models with real data"
echo -e "  5. Get predictions!"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
