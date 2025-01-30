import pandas as pd
import numpy as np
from scipy import stats, signal
import sqlite3
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TechnicalSignal:
    signal_type: str  # 'buy', 'sell', 'hold'
    indicator: str    # which indicator generated the signal
    strength: float   # 0 to 1
    price_level: float
    details: Dict

class TechnicalAnalyzer:
    """Technical analysis capabilities"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def analyze_technicals(self, symbol: str, days: int = 90) -> Dict:
        """
        Comprehensive technical analysis
        """
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
                
                # Calculate indicators
                indicators = {
                    'trend_indicators': self._calculate_trend_indicators(df),
                    'momentum_indicators': self._calculate_momentum_indicators(df),
                    'volatility_indicators': self._calculate_volatility_indicators(df),
                    'volume_indicators': self._calculate_volume_indicators(df),
                    'pattern_recognition': self._identify_patterns(df),
                    'support_resistance': self._find_support_resistance_levels(df),
                    'signals': self._generate_technical_signals(df)
                }
                
                return indicators
                
        except Exception as e:
            logger.error(f"Error in technical analysis: {str(e)}")
            return {}

    def _calculate_trend_indicators(self, df: pd.DataFrame) -> Dict:
        """Calculate trend indicators"""
        try:
            # Moving Averages
            df['sma_20'] = df['close'].rolling(window=20).mean()
            df['sma_50'] = df['close'].rolling(window=50).mean()
            df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
            df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
            
            # MACD
            macd_line = df['ema_12'] - df['ema_26']
            signal_line = macd_line.ewm(span=9, adjust=False).mean()
            macd_hist = macd_line - signal_line
            
            # ADX (Average Directional Index)
            adx = self._calculate_adx(df)
            
            # Trend strength and direction
            trend = self._analyze_trend_strength(df)
            
            latest = df.iloc[-1]
            return {
                'moving_averages': {
                    'sma_20': float(latest['sma_20']),
                    'sma_50': float(latest['sma_50']),
                    'ema_12': float(latest['ema_12']),
                    'ema_26': float(latest['ema_26'])
                },
                'macd': {
                    'macd_line': float(macd_line.iloc[-1]),
                    'signal_line': float(signal_line.iloc[-1]),
                    'histogram': float(macd_hist.iloc[-1])
                },
                'adx': float(adx.iloc[-1]),
                'trend_strength': trend['strength'],
                'trend_direction': trend['direction']
            }
            
        except Exception as e:
            logger.error(f"Error calculating trend indicators: {str(e)}")
            return {}

    def _calculate_momentum_indicators(self, df: pd.DataFrame) -> Dict:
        """Calculate momentum indicators"""
        try:
            # RSI
            df['rsi'] = self._calculate_rsi(df['close'])
            
            # Stochastic Oscillator
            df['stoch_k'], df['stoch_d'] = self._calculate_stochastic(
                df['high'], df['low'], df['close']
            )
            
            # ROC (Rate of Change)
            df['roc'] = df['close'].pct_change(periods=12) * 100
            
            # Williams %R
            df['williams_r'] = self._calculate_williams_r(df)
            
            # Money Flow Index
            df['mfi'] = self._calculate_mfi(df)
            
            latest = df.iloc[-1]
            return {
                'rsi': float(latest['rsi']),
                'stochastic': {
                    'k': float(latest['stoch_k']),
                    'd': float(latest['stoch_d'])
                },
                'roc': float(latest['roc']),
                'williams_r': float(latest['williams_r']),
                'mfi': float(latest['mfi'])
            }
            
        except Exception as e:
            logger.error(f"Error calculating momentum indicators: {str(e)}")
            return {}

    def _calculate_volatility_indicators(self, df: pd.DataFrame) -> Dict:
        """Calculate volatility indicators"""
        try:
            # Bollinger Bands
            df['bb_middle'], df['bb_upper'], df['bb_lower'] = \
                self._calculate_bollinger_bands(df['close'])
            
            # ATR (Average True Range)
            df['atr'] = self._calculate_atr(df)
            
            # Keltner Channels
            df['kc_middle'], df['kc_upper'], df['kc_lower'] = \
                self._calculate_keltner_channels(df)
            
            # Volatility metrics
            volatility = self._calculate_volatility_metrics(df)
            
            latest = df.iloc[-1]
            return {
                'bollinger_bands': {
                    'middle': float(latest['bb_middle']),
                    'upper': float(latest['bb_upper']),
                    'lower': float(latest['bb_lower'])
                },
                'atr': float(latest['atr']),
                'keltner_channels': {
                    'middle': float(latest['kc_middle']),
                    'upper': float(latest['kc_upper']),
                    'lower': float(latest['kc_lower'])
                },
                'volatility_metrics': volatility
            }
            
        except Exception as e:
            logger.error(f"Error calculating volatility indicators: {str(e)}")
            return {}

    def _calculate_volume_indicators(self, df: pd.DataFrame) -> Dict:
        """Calculate volume-based indicators"""
        try:
            # OBV (On-Balance Volume)
            df['obv'] = self._calculate_obv(df)
            
            # Volume SMA
            df['volume_sma'] = df['volume'].rolling(window=20).mean()
            
            # Chaikin Money Flow
            df['cmf'] = self._calculate_chaikin_money_flow(df)
            
            # VWAP (Volume Weighted Average Price)
            df['vwap'] = self._calculate_vwap(df)
            
            latest = df.iloc[-1]
            return {
                'obv': float(latest['obv']),
                'volume_sma': float(latest['volume_sma']),
                'cmf': float(latest['cmf']),
                'vwap': float(latest['vwap']),
                'volume_analysis': self._analyze_volume_trends(df)
            }
            
        except Exception as e:
            logger.error(f"Error calculating volume indicators: {str(e)}")
            return {}

    def _identify_patterns(self, df: pd.DataFrame) -> List[Dict]:
        """Identify chart patterns"""
        patterns = []
        
        try:
            # Candlestick patterns
            patterns.extend(self._identify_candlestick_patterns(df))
            
            # Chart patterns
            patterns.extend(self._identify_chart_patterns(df))
            
            # Price patterns
            patterns.extend(self._identify_price_patterns(df))
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error identifying patterns: {str(e)}")
            return []

    def _find_support_resistance_levels(self, df: pd.DataFrame) -> Dict:
        """Find support and resistance levels"""
        try:
            # Calculate pivot points
            pivots = self._calculate_pivot_points(df)
            
            # Find local extrema
            extrema = self._find_local_extrema(df['close'])
            
            # Identify key levels
            levels = self._identify_key_price_levels(df)
            
            return {
                'pivot_points': pivots,
                'support_levels': sorted([level for level in levels if level < df['close'].iloc[-1]]),
                'resistance_levels': sorted([level for level in levels if level > df['close'].iloc[-1]]),
                'strength': self._calculate_level_strength(df, levels)
            }
            
        except Exception as e:
            logger.error(f"Error finding support/resistance levels: {str(e)}")
            return {}

    def _generate_technical_signals(self, df: pd.DataFrame) -> List[TechnicalSignal]:
        """Generate trading signals based on technical analysis"""
        signals = []
        
        try:
            # Trend signals
            signals.extend(self._generate_trend_signals(df))
            
            # Momentum signals
            signals.extend(self._generate_momentum_signals(df))
            
            # Pattern signals
            signals.extend(self._generate_pattern_signals(df))
            
            # Volume signals
            signals.extend(self._generate_volume_signals(df))
            
            return signals
            
        except Exception as e:
            logger.error(f"Error generating technical signals: {str(e)}")
            return []

    # Helper methods for specific calculations
    def _calculate_rsi(self, prices: pd.Series, periods: int = 14) -> pd.Series:
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def _calculate_stochastic(self, high: pd.Series, low: pd.Series, close: pd.Series,
                            k_window: int = 14, d_window: int = 3) -> Tuple[pd.Series, pd.Series]:
        """Calculate Stochastic Oscillator"""
        low_min = low.rolling(window=k_window).min()
        high_max = high.rolling(window=k_window).max()
        k = 100 * ((close - low_min) / (high_max - low_min))
        d = k.rolling(window=d_window).mean()
        return k, d

    def _calculate_bollinger_bands(self, prices: pd.Series, 
                                 window: int = 20, num_std: int = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate Bollinger Bands"""
        middle = prices.rolling(window=window).mean()
        std = prices.rolling(window=window).std()
        upper = middle + (std * num_std)
        lower = middle - (std * num_std)
        return middle, upper, lower

    def _calculate_vwap(self, df: pd.DataFrame) -> pd.Series:
        """Calculate VWAP"""
        return (df['volume'] * (df['high'] + df['low'] + df['close']) / 3).cumsum() / df['volume'].cumsum()

    def _identify_candlestick_patterns(self, df: pd.DataFrame) -> List[Dict]:
        """Identify candlestick patterns"""
        patterns = []
        
        # Doji
        doji_mask = abs(df['close'] - df['open']) <= (df['high'] - df['low']) * 0.1
        doji_indices = df.index[doji_mask]
        
        for idx in doji_indices:
            patterns.append({
                'pattern': 'doji',
                'date': df.iloc[idx]['date'],
                'price': df.iloc[idx]['close']
            })
        
        # Add more patterns...
        return patterns

    def _analyze_volume_trends(self, df: pd.DataFrame) -> Dict:
        """Analyze volume trends"""
        return {
            'average_volume': float(df['volume'].mean()),
            'volume_trend': self._calculate_trend(df['volume']),
            'price_volume_correlation': float(df['close'].corr(df['volume']))
        }

if __name__ == "__main__":
    # Example usage
    analyzer = TechnicalAnalyzer("./data/investsage.db")
    
    # Get comprehensive technical analysis
    analysis = analyzer.analyze_technicals("AAPL", days=90)
    print("\nTechnical Analysis:")
    print(analysis)
    
    # Check specific components
    print("\nTrend Indicators:")
    print(analysis['trend_indicators'])
    
    print("\nMomentum Indicators:")
    print(analysis['momentum_indicators'])
    
    print("\nVolatility Indicators:")
    print(analysis['volatility_indicators'])
    
    print("\nVolume Indicators:")
    print(analysis['volume_indicators'])