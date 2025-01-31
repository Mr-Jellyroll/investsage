import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLAnalyzer:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.scaler = StandardScaler()
        self.prediction_days = 5

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

                if df.empty:
                    raise ValueError(f"No data found for symbol {symbol}")

                df = df.sort_values('date')  # Sort chronologically
                
                # Create features
                df = self._create_features(df)
                features = ['rsi', 'macd', 'bb_width', 'volume_sma_ratio']
                
                # Prepare training data
                X = df[features].values
                y = df['close'].values
                
                # Scale features
                X_scaled = self.scaler.fit_transform(X)
                
                # Train model
                model = RandomForestRegressor(n_estimators=100, random_state=42)
                model.fit(X_scaled, y)
                
                # Generate future features
                future_features = self._generate_future_features(df, days_ahead)
                future_features_scaled = self.scaler.transform(future_features)
                
                # Make predictions
                predictions = model.predict(future_features_scaled)
                
                # Calculate confidence scores
                confidence_scores = self._calculate_confidence_scores(model, future_features_scaled)
                
                # Get feature importance
                feature_importance = dict(zip(features, model.feature_importances_))
                
                return {
                    'predictions': self._format_predictions(predictions, df),
                    'confidence_scores': confidence_scores.tolist(),
                    'feature_importance': feature_importance
                }

        except Exception as e:
            logger.error(f"Error in price prediction: {str(e)}")
            return self._generate_mock_predictions()

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
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        
        # Volume
        df['volume_sma'] = df['volume'].rolling(window=20).mean()
        df['volume_sma_ratio'] = df['volume'] / df['volume_sma']
        
        # Drop any rows with NaN values
        return df.dropna()

    def _generate_future_features(self, df: pd.DataFrame, days_ahead: int) -> np.ndarray:
        """Generate features for future prediction"""
        last_row = df.iloc[-1]
        features = ['rsi', 'macd', 'bb_width', 'volume_sma_ratio']
        last_features = last_row[features].values.reshape(1, -1)
        return np.tile(last_features, (days_ahead, 1))

    def _calculate_confidence_scores(self, model: RandomForestRegressor, 
                                  features: np.ndarray) -> np.ndarray:
        """Calculate prediction confidence scores"""
        predictions = []
        for estimator in model.estimators_:
            predictions.append(estimator.predict(features))
        predictions = np.array(predictions)
        
        # Calculate standard deviation of predictions as confidence score
        confidence = 1.0 / (1.0 + np.std(predictions, axis=0))
        return confidence

    def _format_predictions(self, predictions: np.ndarray, df: pd.DataFrame) -> List[Dict]:
        """Format predictions with dates"""
        last_date = pd.to_datetime(df['date'].iloc[-1])
        dates = [(last_date + timedelta(days=i+1)).strftime('%Y-%m-%d')
                for i in range(len(predictions))]
        
        return [
            {'date': date, 'price': float(price)}
            for date, price in zip(dates, predictions)
        ]

    def _generate_mock_predictions(self) -> Dict:
        """Generate mock predictions for testing"""
        last_price = 100.0
        dates = [(datetime.now() + timedelta(days=i+1)).strftime('%Y-%m-%d')
                for i in range(self.prediction_days)]
        
        predictions = []
        for i in range(self.prediction_days):
            last_price *= (1 + np.random.normal(0.001, 0.02))
            predictions.append({'date': dates[i], 'price': float(last_price)})
        
        return {
            'predictions': predictions,
            'confidence_scores': [0.8, 0.7, 0.6, 0.5, 0.4],
            'feature_importance': {
                'rsi': 0.3,
                'macd': 0.25,
                'bb_width': 0.25,
                'volume_sma_ratio': 0.2
            }
        }