import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import sqlite3
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    
    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def analyze_sentiment(self, symbol: str, days: int = 30) -> Dict:
        """
        Analyze aggregated sentiment data and its market impact
        """
        try:
            with self.get_connection() as conn:
                # Analyze news sentiment
                news_analysis = self._analyze_news_sentiment(conn, symbol, days)
                
                # Analyze social sentiment
                social_analysis = self._analyze_social_sentiment(conn, symbol, days)
                
                # Get SEC filing sentiment
                filing_analysis = self._analyze_filing_sentiment(conn, symbol, days)
                
                # Analyze sentiment impact on price
                sentiment_impact = self._analyze_sentiment_price_impact(conn, symbol, days)
                
                return {
                    'news': news_analysis,
                    'social': social_analysis,
                    'filings': filing_analysis,
                    'price_impact': sentiment_impact,
                    'overall_sentiment': self._calculate_overall_sentiment(
                        news_analysis, social_analysis, filing_analysis
                    )
                }
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}")
            return {}

    def _analyze_news_sentiment(self, conn: sqlite3.Connection, 
                              symbol: str, days: int) -> Dict:
        """Analyze news sentiment trends"""
        df = pd.read_sql_query("""
            SELECT 
                date(published_date) as date,
                AVG(sentiment_score) as avg_sentiment,
                COUNT(*) as article_count
            FROM news_articles 
            WHERE symbol = ?
            AND published_date >= datetime('now', ?)
            GROUP BY date(published_date)
            ORDER BY date
        """, conn, params=[symbol, f'-{days} days'])
        
        if df.empty:
            return {}
            
        return {
            'current_sentiment': float(df['avg_sentiment'].iloc[-1]),
            'sentiment_trend': self._calculate_trend(df['avg_sentiment']),
            'article_count': int(df['article_count'].sum()),
            'sentiment_momentum': self._calculate_sentiment_momentum(df['avg_sentiment']),
            'extreme_days': self._find_extreme_sentiment_days(df)
        }

    def _analyze_social_sentiment(self, conn: sqlite3.Connection, 
                                symbol: str, days: int) -> Dict:
        """Analyze social media sentiment"""
        df = pd.read_sql_query("""
            SELECT 
                date(posted_date) as date,
                AVG(sentiment_score) as avg_sentiment,
                SUM(engagement_count) as total_engagement,
                COUNT(*) as post_count
            FROM social_sentiment 
            WHERE symbol = ?
            AND posted_date >= datetime('now', ?)
            GROUP BY date(posted_date)
            ORDER BY date
        """, conn, params=[symbol, f'-{days} days'])
        
        if df.empty:
            return {}
            
        return {
            'current_sentiment': float(df['avg_sentiment'].iloc[-1]),
            'sentiment_trend': self._calculate_trend(df['avg_sentiment']),
            'total_engagement': int(df['total_engagement'].sum()),
            'engagement_trend': self._calculate_trend(df['total_engagement']),
            'viral_days': self._find_viral_days(df),
            'sentiment_impact': self._calculate_engagement_weighted_sentiment(df)
        }

    def _analyze_filing_sentiment(self, conn: sqlite3.Connection, 
                                symbol: str, days: int) -> Dict:
        """Analyze SEC filing sentiment"""
        df = pd.read_sql_query("""
            SELECT filing_date, filing_type, description
            FROM sec_filings
            WHERE symbol = ?
            AND filing_date >= datetime('now', ?)
            ORDER BY filing_date
        """, conn, params=[symbol, f'-{days} days'])
        
        if df.empty:
            return {}
            
        # Here we could do more sophisticated analysis of filing text
        return {
            'filing_count': len(df),
            'filing_types': df['filing_type'].value_counts().to_dict(),
            'latest_filing_date': df['filing_date'].max(),
        }

    def _analyze_sentiment_price_impact(self, conn: sqlite3.Connection, 
                                      symbol: str, days: int) -> Dict:
        """Analyze how sentiment affects price"""
        # Get price data
        price_df = pd.read_sql_query("""
            SELECT date, close
            FROM historical_prices
            WHERE symbol = ?
            AND date >= date('now', ?)
            ORDER BY date
        """, conn, params=[symbol, f'-{days} days'])
        
        # Get sentiment data
        sent_df = pd.read_sql_query("""
            SELECT 
                date(posted_date) as date,
                AVG(sentiment_score) as sentiment
            FROM (
                SELECT posted_date, sentiment_score
                FROM social_sentiment
                WHERE symbol = ?
                AND posted_date >= datetime('now', ?)
                UNION ALL
                SELECT published_date, sentiment_score
                FROM news_articles
                WHERE symbol = ?
                AND published_date >= datetime('now', ?)
            )
            GROUP BY date(posted_date)
            ORDER BY date
        """, conn, params=[symbol, f'-{days} days', symbol, f'-{days} days'])
        
        if price_df.empty or sent_df.empty:
            return {}
        
        # Merge price and sentiment
        df = price_df.merge(sent_df, on='date', how='left')
        df['price_change'] = df['close'].pct_change()
        
        # Calculate correlations at different lags
        correlations = []
        for lag in range(5):  # Check up to 5 days lag
            correlation = df['sentiment'].shift(lag).corr(df['price_change'])
            correlations.append((lag, correlation))
        
        return {
            'same_day_correlation': float(correlations[0][1]),
            'lag_correlations': correlations[1:],
            'high_impact_days': self._find_high_impact_days(df)
        }

    def _calculate_trend(self, series: pd.Series) -> str:
        """Calculate trend direction and strength"""
        if len(series) < 2:
            return "neutral"
            
        slope = stats.linregress(range(len(series)), series)[0]
        
        if slope > 0.01:
            return "strongly_positive"
        elif slope > 0:
            return "positive"
        elif slope < -0.01:
            return "strongly_negative"
        elif slope < 0:
            return "negative"
        else:
            return "neutral"

    def _calculate_sentiment_momentum(self, sentiment: pd.Series) -> float:
        """Calculate sentiment momentum"""
        if len(sentiment) < 14:
            return 0.0
            
        changes = sentiment.diff()
        gains = changes.clip(lower=0)
        losses = -changes.clip(upper=0)
        
        avg_gain = gains.rolling(window=14).mean().iloc[-1]
        avg_loss = losses.rolling(window=14).mean().iloc[-1]
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def _find_extreme_sentiment_days(self, df: pd.DataFrame) -> List[Dict]:
        """Find days with extreme sentiment"""
        threshold = df['avg_sentiment'].std() * 2
        extreme_days = df[abs(df['avg_sentiment']) > threshold]
        
        return [{
            'date': row['date'],
            'sentiment': float(row['avg_sentiment']),
            'article_count': int(row['article_count'])
        } for _, row in extreme_days.iterrows()]

    def _find_viral_days(self, df: pd.DataFrame) -> List[Dict]:
        """Find days with viral social media activity"""
        threshold = df['total_engagement'].mean() + df['total_engagement'].std() * 2
        viral_days = df[df['total_engagement'] > threshold]
        
        return [{
            'date': row['date'],
            'engagement': int(row['total_engagement']),
            'sentiment': float(row['avg_sentiment'])
        } for _, row in viral_days.iterrows()]

    def _calculate_overall_sentiment(self, news: Dict, social: Dict, 
                                  filings: Dict) -> float:
        """Calculate weighted overall sentiment"""
        weights = {
            'news': 0.4,
            'social': 0.4,
            'filings': 0.2
        }
        
        sentiments = []
        weights_used = []
        
        if 'current_sentiment' in news:
            sentiments.append(news['current_sentiment'])
            weights_used.append(weights['news'])
            
        if 'current_sentiment' in social:
            sentiments.append(social['current_sentiment'])
            weights_used.append(weights['social'])
            
        if not sentiments:
            return 0.0
            
        # Normalize weights
        weights_used = [w/sum(weights_used) for w in weights_used]
        
        return float(np.average(sentiments, weights=weights_used))

    def _find_high_impact_days(self, df: pd.DataFrame) -> List[Dict]:
        """Find days where sentiment strongly impacted price"""
        df['abs_price_change'] = abs(df['price_change'])
        threshold = df['abs_price_change'].mean() + df['abs_price_change'].std()
        
        high_impact = df[df['abs_price_change'] > threshold]
        
        return [{
            'date': row['date'],
            'price_change': float(row['price_change']),
            'sentiment': float(row['sentiment'])
        } for _, row in high_impact.iterrows()]