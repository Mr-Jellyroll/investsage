
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.preprocessing import StandardScaler
import logging
import sqlite3
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLAnalyzer:
    """Machine Learning analysis"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.scaler = StandardScaler()

    def get_connection(self):
        return sqlite3.connect(self.db_path)
        
    def predict_price(self, symbol: str, days_ahead: int = 5) -> Dict:
        """Predict future price movements"""
        try:
            with self.get_connection() as conn:
                # Get historical data
                df = pd.read_sql_query("""
                    SELECT date, open, high, low, close, volume
                    FROM historical_prices 
                    WHERE symbol = ? 
                    ORDER BY date DESC
                    LIMIT 365
                """, conn, params=[symbol])
                
                df = self._create_features(df)
                
                X = df[['rsi', 'macd', 'bb_position', 'volume_ma_ratio']].values
                y = df['close'].values
                
                # Scale features
                X_scaled = self.scaler.fit_transform(X)
                
                # Train model
                model = RandomForestRegressor(n_estimators=100, random_state=42)
                model.fit(X_scaled, y)
                
                # Make predictions
                future_features = self._generate_future_features(df, days_ahead)
                predictions = model.predict(future_features)
                
                return {
                    'predictions': [float(p) for p in predictions],
                    'confidence': float(model.score(X_scaled, y)),
                    'important_features': self._get_feature_importance(model)
                }
        except Exception as e:
            logger.error(f"Error in price prediction: {str(e)}")
            return {
                'predictions': [],
                'confidence': 0.0,
                'important_features': {}
            }
    
    def detect_anomalies(self, symbol: str, lookback_days: int = 90) -> List[Dict]:
        """Detect abnormal price movements"""
        try:
            with self.get_connection() as conn:
                df = pd.read_sql_query("""
                    SELECT date, close, volume
                    FROM historical_prices 
                    WHERE symbol = ? 
                    AND date >= date('now', ?)
                    ORDER BY date
                """, conn, params=[symbol, f'-{lookback_days} days'])
                
                # Anomaly detection
                features = np.column_stack([
                    df['close'].pct_change().fillna(0),
                    df['volume'].pct_change().fillna(0)
                ])
                
                # Train isolation forest
                iso_forest = IsolationForest(contamination=0.1, random_state=42)
                anomalies = iso_forest.fit_predict(features)
                
                # Collect anomaly dates
                anomaly_dates = df[anomalies == -1]['date'].tolist()
                
                return [{
                    'date': date,
                    'price': float(df[df['date'] == date]['close'].iloc[0]),
                    'volume': int(df[df['date'] == date]['volume'].iloc[0])
                } for date in anomaly_dates]
        except Exception as e:
            logger.error(f"Error in anomaly detection: {str(e)}")
            return []

    def _create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create technical features for ML"""
        df = df.copy()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp1 - exp2
        
        # Bollinger Bands
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # Volume
        df['volume_ma'] = df['volume'].rolling(window=20).mean()
        df['volume_ma_ratio'] = df['volume'] / df['volume_ma']
        
        return df.dropna()

    def _generate_future_features(self, df: pd.DataFrame, days_ahead: int) -> np.ndarray:
        """Generate features for future prediction"""
        last_features = df[['rsi', 'macd', 'bb_position', 'volume_ma_ratio']].iloc[0].values
        return np.tile(last_features, (days_ahead, 1))

    def _get_feature_importance(self, model: RandomForestRegressor) -> Dict:
        """Get feature importance scores"""
        features = ['rsi', 'macd', 'bb_position', 'volume_ma_ratio']
        importance = model.feature_importances_
        return dict(zip(features, importance.tolist()))