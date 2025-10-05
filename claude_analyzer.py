#!/usr/bin/env python3
"""
Claude Opus 4.1 Integration for LetsGetCrypto
Provides AI-powered market analysis and insights
"""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd
from loguru import logger

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic library not available. Claude integration disabled.")


class ClaudeAnalyzer:
    """
    Claude Opus 4.1 powered cryptocurrency analysis
    Provides natural language insights, risk assessment, and market interpretation
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Claude Analyzer
        
        Args:
            api_key: Anthropic API key (if None, reads from ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        self.client = None
        self.model = "claude-opus-4-20250514"  # Claude Opus 4.1
        
        if not ANTHROPIC_AVAILABLE:
            logger.warning("Anthropic library not installed. Install with: pip install anthropic")
            return
            
        if self.api_key:
            try:
                self.client = anthropic.Anthropic(api_key=self.api_key)
                logger.success("Claude Opus 4.1 analyzer initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Claude client: {e}")
        else:
            logger.warning("No Anthropic API key provided. Set ANTHROPIC_API_KEY environment variable.")
    
    def is_available(self) -> bool:
        """Check if Claude analysis is available"""
        return ANTHROPIC_AVAILABLE and self.client is not None
    
    def analyze_market_data(self, 
                           coin_name: str,
                           current_price: float,
                           price_change_24h: float,
                           technical_indicators: Dict[str, Any],
                           ml_predictions: Dict[str, Any],
                           fear_greed_index: Optional[int] = None) -> Dict[str, str]:
        """
        Analyze market data using Claude Opus 4.1
        
        Args:
            coin_name: Cryptocurrency name
            current_price: Current price in USD
            price_change_24h: 24h price change percentage
            technical_indicators: Dict with RSI, MACD, moving averages, etc.
            ml_predictions: Dict with ML model predictions and signals
            fear_greed_index: Fear & Greed Index value (0-100)
            
        Returns:
            Dict with analysis results including insights, recommendations, and risk assessment
        """
        if not self.is_available():
            return {
                'analysis': 'Claude analysis not available. Check API key configuration.',
                'recommendation': 'Unable to provide AI-powered recommendation.',
                'risk_assessment': 'Risk assessment unavailable.',
                'key_insights': []
            }
        
        try:
            # Prepare market context
            market_context = self._prepare_market_context(
                coin_name, current_price, price_change_24h,
                technical_indicators, ml_predictions, fear_greed_index
            )
            
            # Create prompt for Claude
            prompt = f"""You are an expert cryptocurrency analyst. Analyze the following market data and provide insights:

{market_context}

Please provide:
1. A comprehensive market analysis (2-3 paragraphs)
2. A clear trading recommendation (BUY/SELL/HOLD) with reasoning
3. Risk assessment and key factors to consider
4. 3-5 key insights in bullet points

Be concise, actionable, and focus on the most important factors. Remember this is for educational purposes only."""

            # Call Claude API
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse response
            response_text = message.content[0].text
            parsed_response = self._parse_claude_response(response_text)
            
            logger.success(f"Claude analysis completed for {coin_name}")
            return parsed_response
            
        except Exception as e:
            logger.error(f"Error in Claude analysis: {e}")
            return {
                'analysis': f'Analysis error: {str(e)}',
                'recommendation': 'Unable to provide recommendation due to error.',
                'risk_assessment': 'Risk assessment unavailable.',
                'key_insights': []
            }
    
    def explain_trading_signal(self,
                               signal: str,
                               confidence: float,
                               technical_reasons: List[str],
                               coin_name: str) -> str:
        """
        Get natural language explanation of a trading signal
        
        Args:
            signal: Trading signal (BUY/SELL/HOLD)
            confidence: Confidence score (0-1)
            technical_reasons: List of technical reasons for the signal
            coin_name: Cryptocurrency name
            
        Returns:
            Natural language explanation
        """
        if not self.is_available():
            return f"Signal: {signal} (confidence: {confidence:.2%}). Claude explanation not available."
        
        try:
            reasons_text = "\n".join([f"- {reason}" for reason in technical_reasons])
            
            prompt = f"""Explain the following trading signal in clear, simple language for someone learning about cryptocurrency trading:

Cryptocurrency: {coin_name}
Signal: {signal}
Confidence: {confidence:.2%}

Technical Reasons:
{reasons_text}

Provide a 2-3 sentence explanation that helps a trader understand WHY this signal was generated and what it means for their decision."""

            message = self.client.messages.create(
                model=self.model,
                max_tokens=300,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            explanation = message.content[0].text.strip()
            logger.success(f"Generated signal explanation for {coin_name}")
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating signal explanation: {e}")
            return f"Signal: {signal} (confidence: {confidence:.2%}). Unable to generate detailed explanation."
    
    def get_risk_insights(self,
                         volatility: float,
                         volume_change: float,
                         market_sentiment: str) -> Dict[str, Any]:
        """
        Get AI-powered risk insights
        
        Args:
            volatility: Price volatility measure
            volume_change: Trading volume change percentage
            market_sentiment: Current market sentiment (e.g., "Fear", "Greed")
            
        Returns:
            Dict with risk level and detailed insights
        """
        if not self.is_available():
            return {
                'risk_level': 'UNKNOWN',
                'risk_score': 0.5,
                'insights': 'Risk analysis not available without Claude API.'
            }
        
        try:
            prompt = f"""Analyze the following risk factors for cryptocurrency trading:

Volatility: {volatility:.4f}
Volume Change: {volume_change:+.2f}%
Market Sentiment: {market_sentiment}

Provide:
1. Risk Level: LOW, MEDIUM, or HIGH
2. Risk Score: 0.0 (lowest) to 1.0 (highest)
3. 2-3 sentences explaining the risk profile and what traders should be aware of

Format your response as:
RISK_LEVEL: [level]
RISK_SCORE: [score]
INSIGHTS: [your analysis]"""

            message = self.client.messages.create(
                model=self.model,
                max_tokens=400,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response = message.content[0].text
            parsed = self._parse_risk_response(response)
            
            logger.success("Generated risk insights")
            return parsed
            
        except Exception as e:
            logger.error(f"Error generating risk insights: {e}")
            return {
                'risk_level': 'UNKNOWN',
                'risk_score': 0.5,
                'insights': f'Error: {str(e)}'
            }
    
    def _prepare_market_context(self,
                               coin_name: str,
                               current_price: float,
                               price_change_24h: float,
                               technical_indicators: Dict[str, Any],
                               ml_predictions: Dict[str, Any],
                               fear_greed_index: Optional[int]) -> str:
        """Prepare market context for Claude analysis"""
        
        context = f"""
CRYPTOCURRENCY: {coin_name}
CURRENT PRICE: ${current_price:,.2f}
24H CHANGE: {price_change_24h:+.2f}%

TECHNICAL INDICATORS:
"""
        # Add available technical indicators
        if 'rsi' in technical_indicators:
            context += f"- RSI: {technical_indicators['rsi']:.2f}\n"
        if 'macd' in technical_indicators:
            context += f"- MACD: {technical_indicators['macd']:.4f}\n"
        if 'sma_7' in technical_indicators and 'sma_25' in technical_indicators:
            context += f"- SMA 7: ${technical_indicators['sma_7']:.2f}\n"
            context += f"- SMA 25: ${technical_indicators['sma_25']:.2f}\n"
        if 'volatility' in technical_indicators:
            context += f"- Volatility: {technical_indicators['volatility']:.4f}\n"
        
        context += f"\nML PREDICTIONS:\n"
        context += f"- Signal: {ml_predictions.get('signal', 'HOLD')}\n"
        context += f"- Confidence: {ml_predictions.get('confidence', 0.5):.2%}\n"
        
        if fear_greed_index is not None:
            sentiment = self._interpret_fear_greed(fear_greed_index)
            context += f"\nMARKET SENTIMENT:\n- Fear & Greed Index: {fear_greed_index}/100 ({sentiment})\n"
        
        return context
    
    def _parse_claude_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Claude's structured response"""
        
        # Try to extract sections from the response
        sections = {
            'analysis': '',
            'recommendation': '',
            'risk_assessment': '',
            'key_insights': []
        }
        
        # Simple parsing - extract main content
        lines = response_text.strip().split('\n')
        current_section = 'analysis'
        
        for line in lines:
            line_lower = line.lower()
            
            if 'recommendation' in line_lower or 'trading recommendation' in line_lower:
                current_section = 'recommendation'
            elif 'risk' in line_lower and 'assessment' in line_lower:
                current_section = 'risk_assessment'
            elif 'key insight' in line_lower or 'insights:' in line_lower:
                current_section = 'key_insights'
            elif line.strip().startswith(('•', '-', '*', '1.', '2.', '3.', '4.', '5.')):
                if current_section == 'key_insights':
                    insight = line.strip().lstrip('•-*123456789. ')
                    if insight:
                        sections['key_insights'].append(insight)
            else:
                if line.strip():
                    if current_section in ['analysis', 'recommendation', 'risk_assessment']:
                        sections[current_section] += line.strip() + ' '
        
        # Clean up
        for key in ['analysis', 'recommendation', 'risk_assessment']:
            sections[key] = sections[key].strip()
        
        # If parsing failed, put everything in analysis
        if not sections['analysis']:
            sections['analysis'] = response_text.strip()
        
        return sections
    
    def _parse_risk_response(self, response: str) -> Dict[str, Any]:
        """Parse risk analysis response"""
        
        risk_level = 'MEDIUM'
        risk_score = 0.5
        insights = ''
        
        lines = response.split('\n')
        for line in lines:
            if 'RISK_LEVEL:' in line:
                risk_level = line.split(':', 1)[1].strip()
            elif 'RISK_SCORE:' in line:
                try:
                    risk_score = float(line.split(':', 1)[1].strip())
                except:
                    pass
            elif 'INSIGHTS:' in line:
                insights = line.split(':', 1)[1].strip()
            elif insights and line.strip():
                insights += ' ' + line.strip()
        
        # If parsing failed, extract from full text
        if not insights:
            insights = response
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'insights': insights.strip()
        }
    
    def _interpret_fear_greed(self, value: int) -> str:
        """Interpret Fear & Greed Index value"""
        if value <= 20:
            return "Extreme Fear"
        elif value <= 40:
            return "Fear"
        elif value <= 60:
            return "Neutral"
        elif value <= 80:
            return "Greed"
        else:
            return "Extreme Greed"
