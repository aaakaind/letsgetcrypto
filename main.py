#!/usr/bin/env python3
"""
Advanced Cryptocurrency Trading and Prediction Tool

This tool fetches data from multiple APIs, performs feature engineering,
trains ML models, and provides trading signals through a PyQt5 GUI.

RISK DISCLOSURE: This tool is for educational purposes only. Cryptocurrency 
trading involves substantial risk and may result in significant financial losses. 
Predictions are not guarantees and should not be used as the sole basis for 
trading decisions. Always conduct your own research and consult with financial 
advisors before making investment decisions.

Data Sources:
- CoinGecko API: Historical price data
- Binance API (via CCXT): Real-time prices and trading
- NewsAPI: Cryptocurrency news sentiment
- Social Media: Simulated sentiment analysis
- Fear & Greed Index: Market sentiment

ML Techniques:
- LSTM Neural Networks for price prediction
- XGBoost for classification signals
- Logistic Regression as baseline
- Ensemble methods for combined signals

Author: Advanced Crypto Trading Tool
"""

import sys
import os
import json
import time
import logging
import threading
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

# Core libraries
import pandas as pd
import numpy as np
import requests
from retrying import retry
import schedule

# GUI libraries
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QPushButton, QLabel, QComboBox, QLineEdit, 
                            QTextEdit, QCheckBox, QSpinBox, QDoubleSpinBox,
                            QTabWidget, QGridLayout, QGroupBox, QMessageBox,
                            QProgressBar, QSplitter, QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QFont, QPixmap

# Plotting
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import seaborn as sns

# Trading and crypto libraries
import ccxt
try:
    from bitcoinlib import wallets, keys
except ImportError:
    wallets = keys = None
    
try:
    from web3 import Web3
except ImportError:
    Web3 = None

# ML libraries
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import xgboost as xgb

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.optimizers import Adam
    TENSORFLOW_AVAILABLE = True
except ImportError:
    tf = keras = Sequential = LSTM = Dense = Dropout = Adam = None
    TENSORFLOW_AVAILABLE = False

# Technical indicators
import ta

# Logging setup
from loguru import logger

# Configure logging
logger.add("crypto_trading.log", rotation="1 week", retention="4 weeks", level="INFO")

class APIError(Exception):
    """Custom exception for API-related errors"""
    pass

class TradingError(Exception):
    """Custom exception for trading-related errors"""
    pass

class WalletError(Exception):
    """Custom exception for wallet-related errors"""
    pass

class DataFetcher:
    """Handles data fetching from multiple cryptocurrency APIs"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CryptoTradingTool/1.0'
        })
        
    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    def fetch_coingecko_data(self, coin_id: str, days: int = 30) -> Optional[pd.DataFrame]:
        """
        Fetch historical price data from CoinGecko API
        
        Args:
            coin_id: CoinGecko coin identifier (e.g., 'bitcoin', 'ethereum')
            days: Number of days of historical data
            
        Returns:
            DataFrame with price, volume, and market cap data
        """
        try:
            logger.info(f"Fetching CoinGecko data for {coin_id}")
            
            # Historical prices
            url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': 'hourly' if days <= 90 else 'daily'
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Convert to DataFrame
            df = pd.DataFrame({
                'timestamp': [x[0] for x in data['prices']],
                'price': [x[1] for x in data['prices']],
                'volume': [x[1] for x in data['total_volumes']],
                'market_cap': [x[1] for x in data['market_caps']]
            })
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            logger.success(f"Successfully fetched {len(df)} records from CoinGecko")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching CoinGecko data: {e}")
            raise APIError(f"CoinGecko API error: {e}")
    
    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    def fetch_fear_greed_index(self) -> Optional[Dict]:
        """
        Fetch Fear & Greed Index data
        
        Returns:
            Dictionary with current fear & greed index value and classification
        """
        try:
            logger.info("Fetching Fear & Greed Index")
            
            url = "https://api.alternative.me/fng/"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if 'data' in data and len(data['data']) > 0:
                current = data['data'][0]
                result = {
                    'value': int(current['value']),
                    'value_classification': current['value_classification'],
                    'timestamp': current['timestamp']
                }
                logger.success(f"Fear & Greed Index: {result['value']} ({result['value_classification']})")
                return result
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching Fear & Greed Index: {e}")
            return {'value': 50, 'value_classification': 'Neutral', 'timestamp': str(int(time.time()))}
    
    def fetch_news_sentiment(self, coin_name: str) -> Dict[str, float]:
        """
        Simulate news sentiment analysis (placeholder for NewsAPI integration)
        
        Args:
            coin_name: Name of the cryptocurrency
            
        Returns:
            Dictionary with sentiment scores
        """
        try:
            logger.info(f"Simulating news sentiment for {coin_name}")
            
            # Simulate sentiment analysis with some randomness
            import random
            random.seed(int(time.time()) % 1000)
            
            sentiment = {
                'positive': random.uniform(0.1, 0.6),
                'negative': random.uniform(0.1, 0.4),
                'neutral': random.uniform(0.3, 0.7)
            }
            
            # Normalize scores
            total = sum(sentiment.values())
            sentiment = {k: v/total for k, v in sentiment.items()}
            
            logger.info(f"News sentiment: {sentiment}")
            return sentiment
            
        except Exception as e:
            logger.error(f"Error in news sentiment: {e}")
            return {'positive': 0.33, 'negative': 0.33, 'neutral': 0.34}
    
    def fetch_social_sentiment(self, coin_symbol: str) -> Dict[str, float]:
        """
        Simulate social media sentiment analysis
        
        Args:
            coin_symbol: Symbol of the cryptocurrency (e.g., 'BTC', 'ETH')
            
        Returns:
            Dictionary with social sentiment scores
        """
        try:
            logger.info(f"Simulating social sentiment for {coin_symbol}")
            
            # Simulate social sentiment with time-based variation
            hour = datetime.now().hour
            base_sentiment = 0.5 + 0.2 * np.sin(hour * np.pi / 12)
            
            sentiment = {
                'bullish': max(0.1, min(0.8, base_sentiment + np.random.normal(0, 0.1))),
                'bearish': max(0.1, min(0.8, (1 - base_sentiment) + np.random.normal(0, 0.1))),
                'volume': np.random.randint(100, 1000)
            }
            
            logger.info(f"Social sentiment: {sentiment}")
            return sentiment
            
        except Exception as e:
            logger.error(f"Error in social sentiment: {e}")
            return {'bullish': 0.5, 'bearish': 0.5, 'volume': 500}

class TechnicalIndicators:
    """Calculate technical indicators for cryptocurrency data"""
    
    @staticmethod
    def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add technical indicators to price data
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with additional technical indicator columns
        """
        try:
            logger.info("Calculating technical indicators")
            
            # Make a copy to avoid modifying original
            df = df.copy()
            
            # Simple Moving Averages
            df['sma_7'] = ta.trend.sma_indicator(df['price'], window=7)
            df['sma_25'] = ta.trend.sma_indicator(df['price'], window=25)
            df['sma_99'] = ta.trend.sma_indicator(df['price'], window=99)
            
            # Exponential Moving Averages
            df['ema_12'] = ta.trend.ema_indicator(df['price'], window=12)
            df['ema_26'] = ta.trend.ema_indicator(df['price'], window=26)
            
            # MACD
            df['macd'] = ta.trend.macd_diff(df['price'])
            df['macd_signal'] = ta.trend.macd_signal(df['price'])
            
            # RSI
            df['rsi'] = ta.momentum.rsi(df['price'], window=14)
            
            # Bollinger Bands
            df['bb_high'] = ta.volatility.bollinger_hband(df['price'])
            df['bb_low'] = ta.volatility.bollinger_lband(df['price'])
            df['bb_middle'] = ta.volatility.bollinger_mavg(df['price'])
            
            # Volatility
            df['volatility'] = df['price'].rolling(window=24).std()
            
            # Volume indicators (if volume data available)
            if 'volume' in df.columns:
                df['volume_sma'] = ta.volume.volume_sma(df['price'], df['volume'], window=20)
                df['vwap'] = ta.volume.volume_weighted_average_price(df['price'], df['price'], df['volume'], df['volume'], window=14)
            
            # Price change features
            df['price_change'] = df['price'].pct_change()
            df['price_change_1h'] = df['price'].pct_change(periods=1)
            df['price_change_24h'] = df['price'].pct_change(periods=24)
            
            # Quarter-end flag (important for institutional trading)
            df['quarter_end'] = df.index.to_series().apply(
                lambda x: 1 if x.month in [3, 6, 9, 12] and x.day >= 28 else 0
            )
            
            # Support and resistance levels
            df['support'] = df['price'].rolling(window=48, center=True).min()
            df['resistance'] = df['price'].rolling(window=48, center=True).max()
            
            logger.success(f"Added technical indicators to {len(df)} records")
            return df
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
            return df

class MLModels:
    """Machine Learning models for cryptocurrency prediction"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_columns = []
        
    def prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare features and targets for ML models
        
        Args:
            df: DataFrame with price and indicator data
            
        Returns:
            Tuple of features (X) and targets (y)
        """
        try:
            logger.info("Preparing ML features")
            
            # Select feature columns (numeric only)
            feature_cols = [col for col in df.columns if col not in ['price'] and df[col].dtype in ['float64', 'int64']]
            
            # Remove columns with too many NaN values
            feature_cols = [col for col in feature_cols if df[col].notna().sum() > len(df) * 0.5]
            
            self.feature_columns = feature_cols
            
            # Prepare features
            X = df[feature_cols].fillna(method='ffill').fillna(0)
            
            # Create target: 1 if price goes up in next period, 0 otherwise
            df['price_next'] = df['price'].shift(-1)
            df['target'] = (df['price_next'] > df['price']).astype(int)
            
            y = df['target'].fillna(0)
            
            # Remove last row (no target available)
            X = X[:-1]
            y = y[:-1]
            
            logger.success(f"Prepared {X.shape[0]} samples with {X.shape[1]} features")
            return X.values, y.values
            
        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            raise
    
    def train_logistic_regression(self, X: np.ndarray, y: np.ndarray) -> float:
        """
        Train Logistic Regression model
        
        Args:
            X: Feature matrix
            y: Target vector
            
        Returns:
            Model accuracy score
        """
        try:
            logger.info("Training Logistic Regression model")
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model
            model = LogisticRegression(random_state=42, max_iter=1000)
            model.fit(X_train_scaled, y_train)
            
            # Evaluate
            y_pred = model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Store model and scaler
            self.models['logistic'] = model
            self.scalers['logistic'] = scaler
            
            logger.success(f"Logistic Regression accuracy: {accuracy:.4f}")
            return accuracy
            
        except Exception as e:
            logger.error(f"Error training Logistic Regression: {e}")
            return 0.0
    
    def train_xgboost(self, X: np.ndarray, y: np.ndarray) -> float:
        """
        Train XGBoost model with GPU acceleration if available
        
        Args:
            X: Feature matrix
            y: Target vector
            
        Returns:
            Model accuracy score
        """
        try:
            logger.info("Training XGBoost model")
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Check for GPU availability
            try:
                # Try GPU training
                model = xgb.XGBClassifier(
                    tree_method='gpu_hist',
                    gpu_id=0,
                    n_estimators=100,
                    max_depth=6,
                    learning_rate=0.1,
                    random_state=42
                )
                logger.info("Using GPU acceleration for XGBoost")
            except:
                # Fallback to CPU
                model = xgb.XGBClassifier(
                    n_estimators=100,
                    max_depth=6,
                    learning_rate=0.1,
                    random_state=42
                )
                logger.info("Using CPU for XGBoost")
            
            # Train model
            model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Store model
            self.models['xgboost'] = model
            
            logger.success(f"XGBoost accuracy: {accuracy:.4f}")
            return accuracy
            
        except Exception as e:
            logger.error(f"Error training XGBoost: {e}")
            return 0.0
    
    def train_lstm(self, df: pd.DataFrame, sequence_length: int = 60) -> float:
        """
        Train LSTM model for price prediction with GPU acceleration
        
        Args:
            df: DataFrame with price data
            sequence_length: Length of input sequences
            
        Returns:
            Model accuracy score (placeholder)
        """
        try:
            if not TENSORFLOW_AVAILABLE:
                logger.warning("TensorFlow not available, skipping LSTM training")
                return 0.0
                
            logger.info("Training LSTM model")
            
            # Check for GPU
            if tf.config.list_physical_devices('GPU'):
                logger.info("Using GPU acceleration for LSTM")
            else:
                logger.info("Using CPU for LSTM")
            
            # Prepare price data
            prices = df['price'].values.reshape(-1, 1)
            
            # Scale prices
            scaler = MinMaxScaler()
            prices_scaled = scaler.fit_transform(prices)
            
            # Create sequences
            X, y = [], []
            for i in range(sequence_length, len(prices_scaled)):
                X.append(prices_scaled[i-sequence_length:i, 0])
                y.append(prices_scaled[i, 0])
            
            X, y = np.array(X), np.array(y)
            X = X.reshape((X.shape[0], X.shape[1], 1))
            
            # Split data
            split_index = int(0.8 * len(X))
            X_train, X_test = X[:split_index], X[split_index:]
            y_train, y_test = y[:split_index], y[split_index:]
            
            # Build LSTM model
            model = Sequential([
                LSTM(50, return_sequences=True, input_shape=(sequence_length, 1)),
                Dropout(0.2),
                LSTM(50, return_sequences=False),
                Dropout(0.2),
                Dense(25),
                Dense(1)
            ])
            
            model.compile(optimizer=Adam(learning_rate=0.001), loss='mean_squared_error')
            
            # Train model
            history = model.fit(X_train, y_train, batch_size=32, epochs=50, 
                              validation_data=(X_test, y_test), verbose=0)
            
            # Store model and scaler
            self.models['lstm'] = model
            self.scalers['lstm'] = scaler
            
            # Calculate a simple accuracy metric
            y_pred = model.predict(X_test)
            
            # Convert to directional accuracy
            y_test_dir = np.diff(scaler.inverse_transform(y_test.reshape(-1, 1)).flatten())
            y_pred_dir = np.diff(scaler.inverse_transform(y_pred.flatten().reshape(-1, 1)).flatten())
            
            directional_accuracy = np.mean((y_test_dir > 0) == (y_pred_dir > 0))
            
            logger.success(f"LSTM directional accuracy: {directional_accuracy:.4f}")
            return directional_accuracy
            
        except Exception as e:
            logger.error(f"Error training LSTM: {e}")
            return 0.0
    
    def get_ensemble_prediction(self, X: np.ndarray) -> Dict[str, float]:
        """
        Get ensemble prediction from all trained models
        
        Args:
            X: Feature matrix for prediction
            
        Returns:
            Dictionary with individual and ensemble predictions
        """
        try:
            predictions = {}
            
            # Logistic Regression prediction
            if 'logistic' in self.models and 'logistic' in self.scalers:
                X_scaled = self.scalers['logistic'].transform(X)
                pred = self.models['logistic'].predict_proba(X_scaled)[:, 1]
                predictions['logistic'] = float(np.mean(pred))
            
            # XGBoost prediction
            if 'xgboost' in self.models:
                pred = self.models['xgboost'].predict_proba(X)[:, 1]
                predictions['xgboost'] = float(np.mean(pred))
            
            # LSTM prediction (simplified)
            if 'lstm' in self.models:
                # For simplicity, use a placeholder prediction
                predictions['lstm'] = 0.5
            
            # Ensemble prediction (weighted average)
            if predictions:
                weights = {'logistic': 0.3, 'xgboost': 0.5, 'lstm': 0.2}
                ensemble_pred = sum(predictions.get(model, 0) * weights.get(model, 0) 
                                  for model in weights)
                predictions['ensemble'] = ensemble_pred
                
                # Generate trading signal
                if ensemble_pred > 0.6:
                    signal = 'BUY'
                elif ensemble_pred < 0.4:
                    signal = 'SELL'
                else:
                    signal = 'HOLD'
                    
                predictions['signal'] = signal
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error getting ensemble prediction: {e}")
            return {'signal': 'HOLD', 'ensemble': 0.5}

class CryptoWallet:
    """Cryptocurrency wallet functionality for Bitcoin and Ethereum testnet"""
    
    def __init__(self):
        self.wallets = {}
        self.addresses = {}
        
    def create_bitcoin_wallet(self, wallet_name: str = "crypto_trading_btc") -> Dict[str, str]:
        """
        Create a Bitcoin testnet wallet
        
        Args:
            wallet_name: Name for the wallet
            
        Returns:
            Dictionary with wallet information
        """
        try:
            if wallets is None:
                logger.warning("bitcoinlib not available, simulating Bitcoin wallet")
                return self._simulate_wallet('bitcoin', wallet_name)
                
            logger.info(f"Creating Bitcoin wallet: {wallet_name}")
            
            # Create or load wallet
            try:
                wallet = wallets.Wallet(wallet_name, network='testnet')
            except:
                # Wallet might already exist
                wallet = wallets.wallet_exists(wallet_name)
                if wallet:
                    wallet = wallets.Wallet(wallet_name, network='testnet')
                else:
                    raise WalletError("Could not create or load Bitcoin wallet")
            
            # Get address
            address = wallet.get_key().address
            
            # Store wallet info
            self.wallets['bitcoin'] = wallet
            self.addresses['bitcoin'] = address
            
            result = {
                'type': 'bitcoin',
                'network': 'testnet',
                'address': address,
                'wallet_name': wallet_name
            }
            
            logger.success(f"Bitcoin wallet created: {address}")
            return result
            
        except Exception as e:
            logger.error(f"Error creating Bitcoin wallet: {e}")
            return self._simulate_wallet('bitcoin', wallet_name)
    
    def create_ethereum_wallet(self) -> Dict[str, str]:
        """
        Create an Ethereum testnet wallet
        
        Returns:
            Dictionary with wallet information
        """
        try:
            if Web3 is None:
                logger.warning("web3 not available, simulating Ethereum wallet")
                return self._simulate_wallet('ethereum', 'eth_wallet')
                
            logger.info("Creating Ethereum wallet")
            
            # Create new account
            from eth_account import Account
            account = Account.create()
            
            # Store wallet info
            self.wallets['ethereum'] = account
            self.addresses['ethereum'] = account.address
            
            result = {
                'type': 'ethereum',
                'network': 'testnet',
                'address': account.address,
                'private_key': account.privateKey.hex()  # In real app, encrypt this!
            }
            
            logger.success(f"Ethereum wallet created: {account.address}")
            return result
            
        except Exception as e:
            logger.error(f"Error creating Ethereum wallet: {e}")
            return self._simulate_wallet('ethereum', 'eth_wallet')
    
    def _simulate_wallet(self, wallet_type: str, wallet_name: str) -> Dict[str, str]:
        """
        Simulate wallet creation when libraries are not available
        
        Args:
            wallet_type: Type of wallet (bitcoin/ethereum)
            wallet_name: Name of the wallet
            
        Returns:
            Simulated wallet information
        """
        import hashlib
        import secrets
        
        # Generate a pseudo-random address
        random_bytes = secrets.token_bytes(32)
        address_hash = hashlib.sha256(random_bytes).hexdigest()
        
        if wallet_type == 'bitcoin':
            address = f"tb1{address_hash[:32]}"  # Testnet bech32 format
        else:  # ethereum
            address = f"0x{address_hash[:40]}"
        
        self.addresses[wallet_type] = address
        
        return {
            'type': wallet_type,
            'network': 'testnet',
            'address': address,
            'wallet_name': wallet_name,
            'simulated': True
        }
    
    def get_balance(self, wallet_type: str) -> float:
        """
        Get wallet balance (simulated for testnet)
        
        Args:
            wallet_type: Type of wallet (bitcoin/ethereum)
            
        Returns:
            Balance in the respective cryptocurrency
        """
        try:
            # In a real implementation, this would query the blockchain
            # For demonstration, return a simulated balance
            balances = {
                'bitcoin': np.random.uniform(0.01, 0.1),  # BTC
                'ethereum': np.random.uniform(0.1, 1.0)   # ETH
            }
            
            balance = balances.get(wallet_type, 0.0)
            logger.info(f"{wallet_type.title()} balance: {balance:.6f}")
            return balance
            
        except Exception as e:
            logger.error(f"Error getting {wallet_type} balance: {e}")
            return 0.0
    
    def get_wallet_info(self) -> Dict[str, Any]:
        """
        Get information about all wallets
        
        Returns:
            Dictionary with wallet information
        """
        info = {}
        
        for wallet_type in ['bitcoin', 'ethereum']:
            if wallet_type in self.addresses:
                info[wallet_type] = {
                    'address': self.addresses[wallet_type],
                    'balance': self.get_balance(wallet_type)
                }
        
        return info

class TradingEngine:
    """Automated trading engine with risk management"""
    
    def __init__(self):
        self.exchange = None
        self.is_testnet = True
        self.positions = {}
        self.trade_log = []
        self.risk_settings = {
            'max_position_size': 0.1,  # 10% of portfolio
            'stop_loss_pct': 0.05,     # 5% stop loss
            'take_profit_pct': 0.15,   # 15% take profit
            'max_daily_trades': 5
        }
        
    def initialize_exchange(self, api_key: str = "", secret: str = "", testnet: bool = True) -> bool:
        """
        Initialize connection to cryptocurrency exchange
        
        Args:
            api_key: Exchange API key
            secret: Exchange API secret
            testnet: Whether to use testnet/sandbox
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not api_key or not secret:
                logger.warning("No API keys provided, using demo mode")
                self.exchange = None
                return True
                
            logger.info("Initializing exchange connection")
            
            # Initialize Binance exchange (most common)
            self.exchange = ccxt.binance({
                'apiKey': api_key,
                'secret': secret,
                'sandbox': testnet,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot'
                }
            })
            
            # Test connection
            balance = self.exchange.fetch_balance()
            logger.success("Exchange connection successful")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing exchange: {e}")
            self.exchange = None
            return False
    
    def execute_trade(self, symbol: str, signal: str, amount: float = None) -> Dict[str, Any]:
        """
        Execute a trade based on ML signal
        
        Args:
            symbol: Trading symbol (e.g., 'BTC/USDT')
            signal: Trading signal ('BUY', 'SELL', 'HOLD')
            amount: Amount to trade (optional)
            
        Returns:
            Dictionary with trade execution results
        """
        try:
            if signal == 'HOLD':
                return {'status': 'no_action', 'signal': signal}
                
            if self.exchange is None:
                return self._simulate_trade(symbol, signal, amount)
            
            logger.info(f"Executing {signal} trade for {symbol}")
            
            # Get current price
            ticker = self.exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            
            # Calculate trade amount if not provided
            if amount is None:
                balance = self.exchange.fetch_balance()
                base_currency = symbol.split('/')[1]  # e.g., 'USDT' from 'BTC/USDT'
                available_balance = balance[base_currency]['free']
                amount = available_balance * self.risk_settings['max_position_size']
            
            # Check daily trade limit
            today_trades = len([t for t in self.trade_log 
                              if t['timestamp'].date() == datetime.now().date()])
            
            if today_trades >= self.risk_settings['max_daily_trades']:
                logger.warning("Daily trade limit reached")
                return {'status': 'trade_limit_reached', 'signal': signal}
            
            # Execute trade
            if signal == 'BUY':
                order = self.exchange.create_market_buy_order(symbol, amount)
            else:  # SELL
                # For sell, we need to have the base currency
                base_currency = symbol.split('/')[0]  # e.g., 'BTC' from 'BTC/USDT'
                balance = self.exchange.fetch_balance()
                available_amount = balance[base_currency]['free']
                
                if available_amount > 0:
                    order = self.exchange.create_market_sell_order(symbol, min(amount, available_amount))
                else:
                    return {'status': 'insufficient_balance', 'signal': signal}
            
            # Log trade
            trade_record = {
                'timestamp': datetime.now(),
                'symbol': symbol,
                'signal': signal,
                'price': current_price,
                'amount': order['amount'],
                'order_id': order['id'],
                'status': order['status']
            }
            
            self.trade_log.append(trade_record)
            
            logger.success(f"Trade executed: {signal} {order['amount']} {symbol} at {current_price}")
            return {'status': 'success', 'order': order, 'trade': trade_record}
            
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            return {'status': 'error', 'error': str(e), 'signal': signal}
    
    def _simulate_trade(self, symbol: str, signal: str, amount: float = None) -> Dict[str, Any]:
        """
        Simulate trade execution for demo purposes
        
        Args:
            symbol: Trading symbol
            signal: Trading signal
            amount: Amount to trade
            
        Returns:
            Simulated trade results
        """
        try:
            # Simulate current price
            current_price = np.random.uniform(30000, 50000) if 'BTC' in symbol else np.random.uniform(2000, 3000)
            
            # Simulate trade amount
            if amount is None:
                amount = np.random.uniform(0.001, 0.01)
            
            # Create simulated trade record
            trade_record = {
                'timestamp': datetime.now(),
                'symbol': symbol,
                'signal': signal,
                'price': current_price,
                'amount': amount,
                'order_id': f"sim_{int(time.time())}",
                'status': 'filled',
                'simulated': True
            }
            
            self.trade_log.append(trade_record)
            
            logger.info(f"Simulated trade: {signal} {amount} {symbol} at {current_price}")
            return {'status': 'simulated', 'trade': trade_record}
            
        except Exception as e:
            logger.error(f"Error simulating trade: {e}")
            return {'status': 'error', 'error': str(e), 'signal': signal}
    
    def get_trade_history(self) -> List[Dict[str, Any]]:
        """
        Get trading history
        
        Returns:
            List of trade records
        """
        return self.trade_log.copy()
    
    def calculate_portfolio_performance(self) -> Dict[str, float]:
        """
        Calculate portfolio performance metrics
        
        Returns:
            Dictionary with performance metrics
        """
        try:
            if not self.trade_log:
                return {'total_return': 0.0, 'win_rate': 0.0, 'total_trades': 0}
            
            # Simple performance calculation
            buy_trades = [t for t in self.trade_log if t['signal'] == 'BUY']
            sell_trades = [t for t in self.trade_log if t['signal'] == 'SELL']
            
            total_return = 0.0
            wins = 0
            total_pairs = min(len(buy_trades), len(sell_trades))
            
            for i in range(total_pairs):
                buy_price = buy_trades[i]['price']
                sell_price = sell_trades[i]['price']
                return_pct = (sell_price - buy_price) / buy_price
                total_return += return_pct
                
                if return_pct > 0:
                    wins += 1
            
            win_rate = wins / total_pairs if total_pairs > 0 else 0.0
            
            return {
                'total_return': total_return,
                'win_rate': win_rate,
                'total_trades': len(self.trade_log),
                'trade_pairs': total_pairs
            }
            
        except Exception as e:
            logger.error(f"Error calculating performance: {e}")
            return {'total_return': 0.0, 'win_rate': 0.0, 'total_trades': 0}

class CryptoPredictionApp(QMainWindow):
    """Main PyQt5 GUI application"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Cryptocurrency Trading & Prediction Tool")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize components
        self.data_fetcher = DataFetcher()
        self.ml_models = MLModels()
        self.wallet = CryptoWallet()
        self.trading_engine = TradingEngine()
        
        # Data storage
        self.current_data = None
        self.predictions = {}
        
        # Setup UI
        self.setup_ui()
        
        # Setup timers for updates
        self.setup_timers()
        
        # Show risk disclosure
        self.show_risk_disclosure()
        
    def setup_ui(self):
        """Setup the main user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Controls
        left_panel = self.create_control_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Charts and data
        right_panel = self.create_data_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([400, 1000])
        
    def create_control_panel(self) -> QWidget:
        """Create the left control panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Cryptocurrency selection
        coin_group = QGroupBox("Cryptocurrency Selection")
        coin_layout = QVBoxLayout(coin_group)
        
        self.coin_combo = QComboBox()
        self.coin_combo.addItems(['bitcoin', 'ethereum', 'binancecoin', 'cardano', 'solana'])
        coin_layout.addWidget(QLabel("Select Cryptocurrency:"))
        coin_layout.addWidget(self.coin_combo)
        
        layout.addWidget(coin_group)
        
        # Data controls
        data_group = QGroupBox("Data Controls")
        data_layout = QVBoxLayout(data_group)
        
        self.days_spinbox = QSpinBox()
        self.days_spinbox.setRange(7, 365)
        self.days_spinbox.setValue(30)
        data_layout.addWidget(QLabel("Days of data:"))
        data_layout.addWidget(self.days_spinbox)
        
        self.refresh_button = QPushButton("Refresh Data")
        self.refresh_button.clicked.connect(self.refresh_data)
        data_layout.addWidget(self.refresh_button)
        
        layout.addWidget(data_group)
        
        # ML Controls
        ml_group = QGroupBox("Machine Learning")
        ml_layout = QVBoxLayout(ml_group)
        
        self.train_button = QPushButton("Train Models")
        self.train_button.clicked.connect(self.train_models)
        ml_layout.addWidget(self.train_button)
        
        self.predict_button = QPushButton("Get Predictions")
        self.predict_button.clicked.connect(self.get_predictions)
        ml_layout.addWidget(self.predict_button)
        
        layout.addWidget(ml_group)
        
        # Trading controls
        trading_group = QGroupBox("Trading Controls")
        trading_layout = QVBoxLayout(trading_group)
        
        # API Key inputs
        trading_layout.addWidget(QLabel("Binance API Key:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        trading_layout.addWidget(self.api_key_input)
        
        trading_layout.addWidget(QLabel("Binance Secret:"))
        self.api_secret_input = QLineEdit()
        self.api_secret_input.setEchoMode(QLineEdit.Password)
        trading_layout.addWidget(self.api_secret_input)
        
        self.testnet_checkbox = QCheckBox("Use Testnet/Sandbox")
        self.testnet_checkbox.setChecked(True)
        trading_layout.addWidget(self.testnet_checkbox)
        
        self.connect_exchange_button = QPushButton("Connect to Exchange")
        self.connect_exchange_button.clicked.connect(self.connect_exchange)
        trading_layout.addWidget(self.connect_exchange_button)
        
        # Auto-trading toggle
        self.auto_trade_checkbox = QCheckBox("Enable Auto-Trading")
        trading_layout.addWidget(self.auto_trade_checkbox)
        
        # Manual trade button
        self.manual_trade_button = QPushButton("Execute Manual Trade")
        self.manual_trade_button.clicked.connect(self.execute_manual_trade)
        trading_layout.addWidget(self.manual_trade_button)
        
        layout.addWidget(trading_group)
        
        # Wallet controls
        wallet_group = QGroupBox("Wallet Information")
        wallet_layout = QVBoxLayout(wallet_group)
        
        self.create_wallets_button = QPushButton("Create Wallets")
        self.create_wallets_button.clicked.connect(self.create_wallets)
        wallet_layout.addWidget(self.create_wallets_button)
        
        self.wallet_info_text = QTextEdit()
        self.wallet_info_text.setMaximumHeight(100)
        self.wallet_info_text.setReadOnly(True)
        wallet_layout.addWidget(self.wallet_info_text)
        
        layout.addWidget(wallet_group)
        
        # Status and logs
        status_group = QGroupBox("Status & Logs")
        status_layout = QVBoxLayout(status_group)
        
        self.status_label = QLabel("Ready")
        status_layout.addWidget(self.status_label)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        status_layout.addWidget(self.log_text)
        
        layout.addWidget(status_group)
        
        # Add stretch to push everything to top
        layout.addStretch()
        
        return panel
    
    def create_data_panel(self) -> QWidget:
        """Create the right data panel with tabs"""
        tab_widget = QTabWidget()
        
        # Charts tab
        charts_tab = QWidget()
        charts_layout = QVBoxLayout(charts_tab)
        
        # Create matplotlib figure
        self.figure = Figure(figsize=(12, 8))
        self.canvas = FigureCanvas(self.figure)
        charts_layout.addWidget(self.canvas)
        
        tab_widget.addTab(charts_tab, "Price Charts")
        
        # Predictions tab
        predictions_tab = QWidget()
        predictions_layout = QVBoxLayout(predictions_tab)
        
        self.predictions_text = QTextEdit()
        self.predictions_text.setReadOnly(True)
        predictions_layout.addWidget(self.predictions_text)
        
        tab_widget.addTab(predictions_tab, "Predictions & Signals")
        
        # Trading history tab
        trading_tab = QWidget()
        trading_layout = QVBoxLayout(trading_tab)
        
        self.trading_table = QTableWidget()
        trading_layout.addWidget(self.trading_table)
        
        tab_widget.addTab(trading_tab, "Trading History")
        
        return tab_widget
    
    def setup_timers(self):
        """Setup timers for periodic updates"""
        # Auto-refresh timer (every 5 minutes)
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.auto_refresh)
        self.refresh_timer.start(300000)  # 5 minutes
        
        # Status update timer (every 10 seconds)
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(10000)  # 10 seconds
    
    def show_risk_disclosure(self):
        """Show risk disclosure dialog"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Risk Disclosure")
        msg.setText("IMPORTANT RISK DISCLOSURE")
        msg.setInformativeText(
            "This tool is for educational purposes only. Cryptocurrency trading "
            "involves substantial risk and may result in significant financial losses. "
            "Predictions are not guarantees and should not be used as the sole basis "
            "for trading decisions. Always conduct your own research and consult with "
            "financial advisors before making investment decisions.\n\n"
            "By using this tool, you acknowledge these risks."
        )
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    
    def refresh_data(self):
        """Refresh cryptocurrency data"""
        try:
            self.status_label.setText("Fetching data...")
            self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Refreshing data...")
            
            coin_id = self.coin_combo.currentText()
            days = self.days_spinbox.value()
            
            # Fetch price data
            price_data = self.data_fetcher.fetch_coingecko_data(coin_id, days)
            
            if price_data is not None:
                # Add technical indicators
                self.current_data = TechnicalIndicators.add_technical_indicators(price_data)
                
                # Fetch sentiment data
                fear_greed = self.data_fetcher.fetch_fear_greed_index()
                news_sentiment = self.data_fetcher.fetch_news_sentiment(coin_id)
                social_sentiment = self.data_fetcher.fetch_social_sentiment(coin_id.upper()[:3])
                
                # Update charts
                self.update_charts()
                
                self.status_label.setText(f"Data updated: {len(self.current_data)} records")
                self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Data refresh complete")
            else:
                self.status_label.setText("Data fetch failed")
                self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Data fetch failed")
                
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Error: {str(e)}")
    
    def update_charts(self):
        """Update the price charts"""
        if self.current_data is None:
            return
            
        try:
            self.figure.clear()
            
            # Create subplots
            ax1 = self.figure.add_subplot(3, 1, 1)
            ax2 = self.figure.add_subplot(3, 1, 2)
            ax3 = self.figure.add_subplot(3, 1, 3)
            
            data = self.current_data.dropna()
            
            # Price chart with moving averages
            ax1.plot(data.index, data['price'], label='Price', linewidth=2)
            if 'sma_7' in data.columns:
                ax1.plot(data.index, data['sma_7'], label='SMA 7', alpha=0.7)
            if 'sma_25' in data.columns:
                ax1.plot(data.index, data['sma_25'], label='SMA 25', alpha=0.7)
            
            ax1.set_title(f'{self.coin_combo.currentText().title()} Price Chart')
            ax1.set_ylabel('Price (USD)')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # RSI
            if 'rsi' in data.columns:
                ax2.plot(data.index, data['rsi'], label='RSI', color='orange')
                ax2.axhline(y=70, color='r', linestyle='--', alpha=0.5, label='Overbought')
                ax2.axhline(y=30, color='g', linestyle='--', alpha=0.5, label='Oversold')
                ax2.set_ylabel('RSI')
                ax2.set_ylim(0, 100)
                ax2.legend()
                ax2.grid(True, alpha=0.3)
            
            # Volume
            if 'volume' in data.columns:
                ax3.bar(data.index, data['volume'], alpha=0.6, label='Volume')
                ax3.set_ylabel('Volume')
                ax3.legend()
                ax3.grid(True, alpha=0.3)
            
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            logger.error(f"Error updating charts: {e}")
    
    def train_models(self):
        """Train machine learning models"""
        if self.current_data is None:
            self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] No data available for training")
            return
            
        try:
            self.status_label.setText("Training models...")
            self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Starting model training...")
            
            # Prepare features
            X, y = self.ml_models.prepare_features(self.current_data)
            
            # Train models
            lr_accuracy = self.ml_models.train_logistic_regression(X, y)
            xgb_accuracy = self.ml_models.train_xgboost(X, y)
            lstm_accuracy = self.ml_models.train_lstm(self.current_data)
            
            self.status_label.setText("Models trained successfully")
            self.log_text.append(
                f"[{datetime.now().strftime('%H:%M:%S')}] Training complete - "
                f"LR: {lr_accuracy:.3f}, XGB: {xgb_accuracy:.3f}, LSTM: {lstm_accuracy:.3f}"
            )
            
        except Exception as e:
            self.status_label.setText(f"Training error: {str(e)}")
            self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Training error: {str(e)}")
    
    def get_predictions(self):
        """Get ML predictions and trading signals"""
        if self.current_data is None:
            self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] No data available for predictions")
            return
            
        try:
            self.status_label.setText("Generating predictions...")
            
            # Prepare latest features
            X, _ = self.ml_models.prepare_features(self.current_data)
            
            if len(X) > 0:
                # Get ensemble prediction
                self.predictions = self.ml_models.get_ensemble_prediction(X[-10:])  # Last 10 samples
                
                # Update predictions display
                self.update_predictions_display()
                
                self.status_label.setText("Predictions updated")
                self.log_text.append(
                    f"[{datetime.now().strftime('%H:%M:%S')}] Predictions: "
                    f"Signal={self.predictions.get('signal', 'HOLD')}, "
                    f"Confidence={self.predictions.get('ensemble', 0.5):.3f}"
                )
                
                # Auto-trade if enabled
                if self.auto_trade_checkbox.isChecked():
                    self.execute_auto_trade()
            
        except Exception as e:
            self.status_label.setText(f"Prediction error: {str(e)}")
            self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Prediction error: {str(e)}")
    
    def update_predictions_display(self):
        """Update the predictions display"""
        if not self.predictions:
            return
            
        display_text = f"""
CRYPTOCURRENCY PREDICTIONS & TRADING SIGNALS
===========================================

Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Cryptocurrency: {self.coin_combo.currentText().title()}

ML MODEL PREDICTIONS:
--------------------
Logistic Regression: {self.predictions.get('logistic', 'N/A'):.4f}
XGBoost: {self.predictions.get('xgboost', 'N/A'):.4f}
LSTM: {self.predictions.get('lstm', 'N/A'):.4f}

ENSEMBLE PREDICTION:
-------------------
Confidence Score: {self.predictions.get('ensemble', 0.5):.4f}
Trading Signal: {self.predictions.get('signal', 'HOLD')}

SIGNAL INTERPRETATION:
---------------------
BUY: High confidence upward price movement expected
SELL: High confidence downward price movement expected  
HOLD: Uncertain market conditions, maintain current position

RISK DISCLAIMER:
---------------
These predictions are based on historical data and technical indicators.
They are NOT guaranteed and should not be used as the sole basis for
trading decisions. Always conduct your own research.
        """
        
        self.predictions_text.setText(display_text)
    
    def connect_exchange(self):
        """Connect to cryptocurrency exchange"""
        api_key = self.api_key_input.text().strip()
        api_secret = self.api_secret_input.text().strip()
        testnet = self.testnet_checkbox.isChecked()
        
        success = self.trading_engine.initialize_exchange(api_key, api_secret, testnet)
        
        if success:
            self.status_label.setText("Exchange connected")
            self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Exchange connected successfully")
        else:
            self.status_label.setText("Exchange connection failed")
            self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Exchange connection failed")
    
    def execute_manual_trade(self):
        """Execute a manual trade based on current signal"""
        if not self.predictions:
            self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] No predictions available")
            return
            
        coin_symbol = self.coin_combo.currentText().upper()
        if coin_symbol == 'BITCOIN':
            symbol = 'BTC/USDT'
        elif coin_symbol == 'ETHEREUM':
            symbol = 'ETH/USDT'
        else:
            symbol = f'{coin_symbol[:3]}/USDT'
        
        signal = self.predictions.get('signal', 'HOLD')
        
        result = self.trading_engine.execute_trade(symbol, signal)
        
        self.log_text.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] Trade executed: "
            f"{signal} {symbol} - Status: {result.get('status', 'unknown')}"
        )
        
        self.update_trading_history()
    
    def execute_auto_trade(self):
        """Execute automatic trading based on ML signals"""
        if not self.predictions:
            return
            
        # Only trade if confidence is high enough
        confidence = self.predictions.get('ensemble', 0.5)
        if confidence < 0.3 or confidence > 0.7:  # High confidence threshold
            self.execute_manual_trade()
    
    def create_wallets(self):
        """Create cryptocurrency wallets"""
        try:
            self.status_label.setText("Creating wallets...")
            
            # Create Bitcoin wallet
            btc_wallet = self.wallet.create_bitcoin_wallet()
            
            # Create Ethereum wallet
            eth_wallet = self.wallet.create_ethereum_wallet()
            
            # Update wallet info display
            wallet_info = self.wallet.get_wallet_info()
            
            info_text = "CRYPTOCURRENCY WALLETS\n"
            info_text += "=====================\n\n"
            
            for wallet_type, info in wallet_info.items():
                info_text += f"{wallet_type.title()}:\n"
                info_text += f"Address: {info['address']}\n"
                info_text += f"Balance: {info['balance']:.6f}\n\n"
            
            info_text += "NOTE: These are testnet wallets for demonstration purposes.\n"
            info_text += "Do not send real cryptocurrency to these addresses."
            
            self.wallet_info_text.setText(info_text)
            
            self.status_label.setText("Wallets created")
            self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Wallets created successfully")
            
        except Exception as e:
            self.status_label.setText(f"Wallet error: {str(e)}")
            self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Wallet error: {str(e)}")
    
    def update_trading_history(self):
        """Update the trading history table"""
        trades = self.trading_engine.get_trade_history()
        
        self.trading_table.setRowCount(len(trades))
        self.trading_table.setColumnCount(6)
        self.trading_table.setHorizontalHeaderLabels([
            'Timestamp', 'Symbol', 'Signal', 'Price', 'Amount', 'Status'
        ])
        
        for i, trade in enumerate(trades):
            self.trading_table.setItem(i, 0, QTableWidgetItem(trade['timestamp'].strftime('%Y-%m-%d %H:%M:%S')))
            self.trading_table.setItem(i, 1, QTableWidgetItem(trade['symbol']))
            self.trading_table.setItem(i, 2, QTableWidgetItem(trade['signal']))
            self.trading_table.setItem(i, 3, QTableWidgetItem(f"{trade['price']:.2f}"))
            self.trading_table.setItem(i, 4, QTableWidgetItem(f"{trade['amount']:.6f}"))
            self.trading_table.setItem(i, 5, QTableWidgetItem(trade['status']))
        
        self.trading_table.resizeColumnsToContents()
    
    def auto_refresh(self):
        """Auto-refresh data periodically"""
        if self.current_data is not None:  # Only refresh if we have data
            self.refresh_data()
    
    def update_status(self):
        """Update status information"""
        # Update portfolio performance if we have trades
        trades = self.trading_engine.get_trade_history()
        if trades:
            performance = self.trading_engine.calculate_portfolio_performance()
            self.log_text.append(
                f"[{datetime.now().strftime('%H:%M:%S')}] Portfolio: "
                f"Return={performance['total_return']:.2%}, "
                f"Win Rate={performance['win_rate']:.2%}, "
                f"Trades={performance['total_trades']}"
            )

def main():
    """Main application entry point"""
    
    # Display startup information
    print("=" * 60)
    print("ADVANCED CRYPTOCURRENCY TRADING & PREDICTION TOOL")
    print("=" * 60)
    print("\nStarting application...")
    print("\nData Sources:")
    print("- CoinGecko API (Historical price data)")
    print("- Binance API via CCXT (Real-time trading)")
    print("- Simulated news sentiment analysis")
    print("- Simulated social media sentiment")
    print("- Fear & Greed Index")
    print("\nML Models:")
    print("- LSTM Neural Networks")
    print("- XGBoost Classifier")
    print("- Logistic Regression")
    print("- Ensemble prediction")
    print("\nFeatures:")
    print("- Technical indicators")
    print("- Risk management")
    print("- Wallet integration")
    print("- Automated trading")
    print("\n" + "=" * 60)
    
    # Create QApplication
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = CryptoPredictionApp()
    window.show()
    
    # Log startup
    logger.info("Cryptocurrency Trading & Prediction Tool started successfully")
    
    # Run application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()