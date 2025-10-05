#!/usr/bin/env python3
"""
Headless version of the LetsGetCrypto trading tool for AWS deployment
This version runs without GUI and provides a REST API interface
"""

import os
import sys
import json
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

# Core libraries
import pandas as pd
import numpy as np
import requests
from retrying import retry

# ML libraries
try:
    import sklearn
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import accuracy_score, classification_report
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️ ML libraries not available. Using simplified mode.")

# Technical analysis
try:
    import ta
    TA_AVAILABLE = True
except ImportError:
    TA_AVAILABLE = False
    print("⚠️ Technical analysis library not available.")

# Claude integration
try:
    from claude_analyzer import ClaudeAnalyzer
    CLAUDE_AVAILABLE = True
except ImportError:
    ClaudeAnalyzer = None
    CLAUDE_AVAILABLE = False
    print("⚠️ Claude Analyzer not available. AI insights disabled.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HeadlessCryptoAPI:
    """
    Headless version of the crypto trading tool
    Provides API-like interface for AWS deployment
    """
    
    def __init__(self, enable_claude: bool = True):
        self.data_cache = {}
        self.cache_timeout = 300  # 5 minutes
        self.supported_coins = [
            'bitcoin', 'ethereum', 'binancecoin', 'cardano', 'solana',
            'polkadot', 'dogecoin', 'avalanche-2', 'polygon', 'chainlink'
        ]
        
        # Initialize Claude analyzer if available and enabled
        self.claude_analyzer = None
        if enable_claude and CLAUDE_AVAILABLE:
            self.claude_analyzer = ClaudeAnalyzer()
            if self.claude_analyzer.is_available():
                logger.info("Claude Opus 4.1 integration enabled")
            else:
                logger.warning("Claude API key not configured. AI insights disabled.")
        
    def fetch_price_data(self, coin_id: str, days: int = 30) -> Optional[pd.DataFrame]:
        """
        Fetch price data from CoinGecko API
        """
        cache_key = f"{coin_id}_{days}"
        
        # Check cache
        if cache_key in self.data_cache:
            cached_data, timestamp = self.data_cache[cache_key]
            if time.time() - timestamp < self.cache_timeout:
                logger.info(f"Using cached data for {coin_id}")
                return cached_data
        
        try:
            logger.info(f"Fetching data for {coin_id} ({days} days)")
            
            url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': 'daily' if days > 30 else 'hourly'
            }
            
            response = requests.get(url, params=params, timeout=30)
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
            
            # Cache the data
            self.data_cache[cache_key] = (df, time.time())
            
            logger.info(f"Successfully fetched {len(df)} records for {coin_id}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data for {coin_id}: {e}")
            return None
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators
        """
        if not TA_AVAILABLE:
            logger.warning("Technical analysis not available, using basic indicators")
            df['sma_7'] = df['price'].rolling(7).mean()
            df['sma_25'] = df['price'].rolling(25).mean()
            df['price_change'] = df['price'].pct_change()
            df['volatility'] = df['price_change'].rolling(7).std()
            return df
        
        try:
            logger.info("Calculating technical indicators")
            
            # Simple Moving Averages
            df['sma_7'] = ta.trend.sma_indicator(df['price'], window=7)
            df['sma_25'] = ta.trend.sma_indicator(df['price'], window=25)
            
            # RSI
            df['rsi'] = ta.momentum.rsi(df['price'], window=14)
            
            # MACD
            df['macd'] = ta.trend.macd_diff(df['price'])
            
            # Bollinger Bands
            bb_high = ta.volatility.bollinger_hband(df['price'])
            bb_low = ta.volatility.bollinger_lband(df['price'])
            df['bb_width'] = (bb_high - bb_low) / df['price']
            
            # Volume indicators
            df['volume_sma'] = ta.volume.volume_sma(df['volume'], window=7)
            
            # Price changes
            df['price_change'] = df['price'].pct_change()
            df['volatility'] = df['price_change'].rolling(7).std()
            
            logger.info("Technical indicators calculated successfully")
            return df
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
            # Fallback to basic indicators
            df['sma_7'] = df['price'].rolling(7).mean()
            df['sma_25'] = df['price'].rolling(25).mean()
            df['price_change'] = df['price'].pct_change()
            df['volatility'] = df['price_change'].rolling(7).std()
            return df
    
    def generate_signals(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate trading signals based on technical analysis
        """
        if len(df) < 25:
            return {'signal': 'HOLD', 'confidence': 0.0, 'reason': 'Insufficient data'}
        
        try:
            latest = df.iloc[-1]
            signals = []
            reasons = []
            
            # Moving average crossover
            if latest['sma_7'] > latest['sma_25']:
                signals.append(1)  # Buy signal
                reasons.append("SMA7 > SMA25")
            else:
                signals.append(-1)  # Sell signal
                reasons.append("SMA7 < SMA25")
            
            # RSI signals
            if 'rsi' in df.columns:
                rsi = latest['rsi']
                if rsi < 30:
                    signals.append(1)  # Oversold - buy
                    reasons.append(f"RSI oversold ({rsi:.1f})")
                elif rsi > 70:
                    signals.append(-1)  # Overbought - sell
                    reasons.append(f"RSI overbought ({rsi:.1f})")
                else:
                    signals.append(0)  # Neutral
            
            # Volume analysis
            if 'volume_sma' in df.columns and latest['volume'] > latest['volume_sma'] * 1.5:
                signals.append(1)  # High volume - bullish
                reasons.append("High volume")
            
            # Volatility analysis
            if latest['volatility'] > df['volatility'].quantile(0.8):
                signals.append(0)  # High volatility - hold
                reasons.append("High volatility")
            
            # Calculate overall signal
            avg_signal = np.mean(signals) if signals else 0
            confidence = min(abs(avg_signal), 1.0)
            
            if avg_signal > 0.3:
                signal = 'BUY'
            elif avg_signal < -0.3:
                signal = 'SELL'
            else:
                signal = 'HOLD'
            
            return {
                'signal': signal,
                'confidence': confidence,
                'reasons': reasons,
                'price': latest['price'],
                'sma_7': latest['sma_7'],
                'sma_25': latest['sma_25'],
                'rsi': latest.get('rsi', None),
                'volume': latest['volume'],
                'volatility': latest['volatility']
            }
            
        except Exception as e:
            logger.error(f"Error generating signals: {e}")
            return {'signal': 'HOLD', 'confidence': 0.0, 'reason': f'Error: {e}'}
    
    def get_market_overview(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get market overview for top cryptocurrencies
        """
        try:
            logger.info(f"Fetching market overview for top {limit} cryptocurrencies")
            
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': limit,
                'page': 1,
                'sparkline': 'false',
                'price_change_percentage': '24h'
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            market_data = []
            for coin in data:
                market_data.append({
                    'symbol': coin.get('symbol', '').upper(),
                    'name': coin.get('name'),
                    'price_usd': coin.get('current_price'),
                    'market_cap_usd': coin.get('market_cap'),
                    'volume_24h_usd': coin.get('total_volume'),
                    'price_change_24h_percent': coin.get('price_change_percentage_24h'),
                    'market_cap_rank': coin.get('market_cap_rank')
                })
            
            logger.info(f"Successfully fetched market data for {len(market_data)} cryptocurrencies")
            return market_data
            
        except Exception as e:
            logger.error(f"Error fetching market overview: {e}")
            return []
    
    def analyze_cryptocurrency(self, coin_id: str, days: int = 30, use_claude: bool = True) -> Dict[str, Any]:
        """
        Perform complete analysis of a cryptocurrency
        """
        logger.info(f"Starting analysis for {coin_id}")
        
        # Fetch data
        df = self.fetch_price_data(coin_id, days)
        if df is None:
            return {'error': f'Could not fetch data for {coin_id}'}
        
        # Calculate technical indicators
        df = self.calculate_technical_indicators(df)
        
        # Generate signals
        signals = self.generate_signals(df)
        
        # Calculate additional statistics
        latest_price = df['price'].iloc[-1]
        price_change_24h = (latest_price - df['price'].iloc[-2]) / df['price'].iloc[-2] * 100
        
        volatility_7d = df['price_change'].tail(7).std() * np.sqrt(7) * 100
        
        result = {
            'coin_id': coin_id,
            'analysis_timestamp': datetime.now().isoformat(),
            'price_data': {
                'current_price': latest_price,
                'price_change_24h_percent': price_change_24h,
                'volatility_7d_percent': volatility_7d,
                'data_points': len(df)
            },
            'technical_analysis': signals,
            'market_trend': self._determine_trend(df),
            'recommendation': self._get_recommendation(signals)
        }
        
        # Add Claude AI analysis if available and requested
        if use_claude and self.claude_analyzer and self.claude_analyzer.is_available():
            try:
                logger.info("Generating Claude AI analysis...")
                
                # Prepare technical indicators for Claude
                latest_data = df.iloc[-1]
                tech_indicators = {
                    'rsi': latest_data.get('rsi', None),
                    'macd': latest_data.get('macd', None),
                    'sma_7': latest_data.get('sma_7', None),
                    'sma_25': latest_data.get('sma_25', None),
                    'volatility': latest_data.get('volatility', None),
                    'volume': latest_data.get('volume', None)
                }
                
                ml_predictions = {
                    'signal': signals.get('signal', 'HOLD'),
                    'confidence': signals.get('confidence', 0.5)
                }
                
                claude_analysis = self.claude_analyzer.analyze_market_data(
                    coin_name=coin_id.replace('-', ' ').title(),
                    current_price=latest_price,
                    price_change_24h=price_change_24h,
                    technical_indicators=tech_indicators,
                    ml_predictions=ml_predictions,
                    fear_greed_index=None
                )
                
                result['claude_analysis'] = claude_analysis
                logger.success("Claude AI analysis added successfully")
                
            except Exception as e:
                logger.error(f"Error generating Claude analysis: {e}")
                result['claude_analysis'] = {
                    'error': f'Claude analysis failed: {str(e)}'
                }
        
        return result
    
    def _determine_trend(self, df: pd.DataFrame) -> str:
        """Determine market trend"""
        if len(df) < 7:
            return 'INSUFFICIENT_DATA'
        
        recent_prices = df['price'].tail(7)
        trend_slope = np.polyfit(range(len(recent_prices)), recent_prices, 1)[0]
        
        if trend_slope > df['price'].iloc[-1] * 0.01:  # > 1% slope
            return 'BULLISH'
        elif trend_slope < -df['price'].iloc[-1] * 0.01:  # < -1% slope
            return 'BEARISH'
        else:
            return 'SIDEWAYS'
    
    def _get_recommendation(self, signals: Dict[str, Any]) -> str:
        """Get investment recommendation"""
        signal = signals.get('signal', 'HOLD')
        confidence = signals.get('confidence', 0.0)
        
        if signal == 'BUY' and confidence > 0.6:
            return 'STRONG_BUY'
        elif signal == 'BUY':
            return 'WEAK_BUY'
        elif signal == 'SELL' and confidence > 0.6:
            return 'STRONG_SELL'
        elif signal == 'SELL':
            return 'WEAK_SELL'
        else:
            return 'HOLD'


def main():
    """
    Main function for headless operation
    """
    print("🚀 LetsGetCrypto Headless Mode")
    print("=" * 40)
    
    # Initialize API
    api = HeadlessCryptoAPI()
    
    # Test with Bitcoin
    print("\n📊 Testing with Bitcoin analysis...")
    result = api.analyze_cryptocurrency('bitcoin', days=30)
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
    else:
        print(f"✅ Analysis completed for {result['coin_id']}")
        print(f"💰 Current price: ${result['price_data']['current_price']:.2f}")
        print(f"📈 24h change: {result['price_data']['price_change_24h_percent']:.2f}%")
        print(f"📊 Signal: {result['technical_analysis']['signal']}")
        print(f"🎯 Recommendation: {result['recommendation']}")
        print(f"📈 Trend: {result['market_trend']}")
    
    # Test market overview
    print("\n🏪 Testing market overview...")
    market_data = api.get_market_overview(5)
    
    if market_data:
        print("✅ Market overview fetched successfully")
        for coin in market_data[:3]:
            print(f"  {coin['symbol']}: ${coin['price_usd']:.2f} ({coin['price_change_24h_percent']:.2f}%)")
    else:
        print("❌ Failed to fetch market overview")
    
    print("\n✅ Headless mode test completed!")
    print("🔧 System is ready for AWS deployment")


if __name__ == "__main__":
    main()