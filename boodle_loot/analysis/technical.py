import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import sqlite3
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TechnicalAnalyzer:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def analyze_technicals(self, symbol: str, days: int = 90) -> Dict:
        """Analyze technical indicators"""
        try:
            with self.get_connection() as conn:
                # Get historical data
                df = pd.read_sql_query("""
                    SELECT date, open, high, low, close, volume
                    FROM historical_prices 
                    WHERE symbol = ? 
                    AND date >= date('now', ?)
                    ORDER BY date
                """, conn, params=[symbol, f'-{days} days'])

                if df.empty:
                    raise ValueError(f"No data found for symbol {symbol}")

                # Calculate basic indicators
                df['sma_20'] = df['close'].rolling(window=20).mean()
                df['sma_50'] = df['close'].rolling(window=50).mean()
                df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
                df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()

                # Prepare moving averages data
                moving_averages = df.apply(pd.to_numeric, errors='coerce').to_dict('records')

                return {
                    'trend_indicators': {
                        'moving_averages': moving_averages,
                        'trend': self._analyze_trend(df)
                    },
                    'momentum_indicators': self._calculate_momentum(df),
                    'volume_indicators': self._analyze_volume(df)
                }

        except Exception as e:
            logger.error(f"Error in technical analysis: {str(e)}")
            return {
                'trend_indicators': {
                    'moving_averages': [],
                    'trend': 'neutral'
                },
                'momentum_indicators': {},
                'volume_indicators': {}
            }

    def _analyze_trend(self, df: pd.DataFrame) -> str:
        """Analyze price trend"""
        try:
            # Simple trend analysis using last 20 days
            recent_prices = df['close'].tail(20)
            if len(recent_prices) < 2:
                return 'neutral'

            slope = (recent_prices.iloc[-1] - recent_prices.iloc[0]) / len(recent_prices)
            if slope > 0.01:
                return 'uptrend'
            elif slope < -0.01:
                return 'downtrend'
            return 'neutral'

        except Exception as e:
            logger.error(f"Error analyzing trend: {str(e)}")
            return 'neutral'

    def _calculate_momentum(self, df: pd.DataFrame) -> Dict:
        """Calculate momentum indicators"""
        try:
            # RSI calculation
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))

            return {
                'rsi': float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0
            }

        except Exception as e:
            logger.error(f"Error calculating momentum: {str(e)}")
            return {'rsi': 50.0}

    def _analyze_volume(self, df: pd.DataFrame) -> Dict:
        """Analyze volume trends"""
        try:
            avg_volume = df['volume'].mean()
            recent_volume = df['volume'].tail(5).mean()
            volume_trend = 'increasing' if recent_volume > avg_volume else 'decreasing'

            return {
                'average_volume': float(avg_volume),
                'volume_trend': volume_trend
            }

        except Exception as e:
            logger.error(f"Error analyzing volume: {str(e)}")
            return {
                'average_volume': 0,
                'volume_trend': 'neutral'
            }