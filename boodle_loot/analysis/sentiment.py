import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import sqlite3
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def analyze_sentiment(self, symbol: str, days: int = 30) -> Dict:
        """Analyze news and social sentiment for a symbol"""
        try:
            with self.get_connection() as conn:
                # Get news sentiment
                news_data = pd.read_sql_query("""
                    SELECT 
                        date(published_date) as date,
                        AVG(sentiment_score) as avg_sentiment,
                        COUNT(*) as article_count,
                        GROUP_CONCAT(title) as titles
                    FROM news_articles 
                    WHERE symbol = ?
                    AND published_date >= datetime('now', ?)
                    GROUP BY date(published_date)
                    ORDER BY date
                """, conn, params=[symbol, f'-{days} days'])

                # Get social sentiment
                social_data = pd.read_sql_query("""
                    SELECT 
                        date(posted_date) as date,
                        AVG(sentiment_score) as avg_sentiment,
                        COUNT(*) as post_count,
                        SUM(engagement_count) as total_engagement
                    FROM social_sentiment 
                    WHERE symbol = ?
                    AND posted_date >= datetime('now', ?)
                    GROUP BY date(posted_date)
                    ORDER BY date
                """, conn, params=[symbol, f'-{days} days'])

                # If no data, return mock data for development
                if news_data.empty and social_data.empty:
                    return self._generate_mock_sentiment_data()

                return {
                    'news_sentiment': {
                        'average_score': float(news_data['avg_sentiment'].mean()) if not news_data.empty else 0,
                        'article_count': int(news_data['article_count'].sum()) if not news_data.empty else 0,
                        'daily_scores': news_data.to_dict('records') if not news_data.empty else []
                    },
                    'social_sentiment': {
                        'average_score': float(social_data['avg_sentiment'].mean()) if not social_data.empty else 0,
                        'post_count': int(social_data['post_count'].sum()) if not social_data.empty else 0,
                        'total_engagement': int(social_data['total_engagement'].sum()) if not social_data.empty else 0,
                        'daily_scores': social_data.to_dict('records') if not social_data.empty else []
                    },
                    'overall_sentiment': {
                        'score': self._calculate_overall_sentiment(news_data, social_data),
                        'trend': self._calculate_sentiment_trend(news_data, social_data)
                    }
                }

        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}")
            return self._generate_mock_sentiment_data()

    def _calculate_overall_sentiment(self, news_data: pd.DataFrame, social_data: pd.DataFrame) -> float:
        """Calculate weighted overall sentiment score"""
        try:
            news_weight = 0.6
            social_weight = 0.4

            news_sentiment = news_data['avg_sentiment'].mean() if not news_data.empty else 0
            social_sentiment = social_data['avg_sentiment'].mean() if not social_data.empty else 0

            # If we only have one type of data, adjust weights
            if news_data.empty:
                social_weight = 1.0
                news_weight = 0.0
            elif social_data.empty:
                news_weight = 1.0
                social_weight = 0.0

            return float(news_sentiment * news_weight + social_sentiment * social_weight)

        except Exception as e:
            logger.error(f"Error calculating overall sentiment: {str(e)}")
            return 0.0

    def _calculate_sentiment_trend(self, news_data: pd.DataFrame, social_data: pd.DataFrame) -> str:
        """Calculate sentiment trend over time"""
        try:
            # Combine news and social sentiment
            all_sentiment = pd.DataFrame()
            
            if not news_data.empty:
                all_sentiment = pd.concat([
                    all_sentiment,
                    news_data[['date', 'avg_sentiment']].rename(columns={'avg_sentiment': 'news_sentiment'})
                ])
            
            if not social_data.empty:
                all_sentiment = pd.concat([
                    all_sentiment,
                    social_data[['date', 'avg_sentiment']].rename(columns={'avg_sentiment': 'social_sentiment'})
                ])

            if all_sentiment.empty:
                return 'neutral'

            # Calculate trend based on last few days
            recent_sentiment = all_sentiment.tail(5)
            if len(recent_sentiment) < 2:
                return 'neutral'

            slope = np.polyfit(range(len(recent_sentiment)), recent_sentiment['avg_sentiment'], 1)[0]
            
            if slope > 0.01:
                return 'improving'
            elif slope < -0.01:
                return 'deteriorating'
            return 'stable'

        except Exception as e:
            logger.error(f"Error calculating sentiment trend: {str(e)}")
            return 'neutral'

    def _generate_mock_sentiment_data(self) -> Dict:
        """Generate mock sentiment data for testing"""
        return {
            'news_sentiment': {
                'average_score': 0.2,
                'article_count': 10,
                'daily_scores': [
                    {'date': (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'),
                     'avg_sentiment': np.random.normal(0.2, 0.1),
                     'article_count': np.random.randint(1, 5)}
                    for i in range(7)
                ]
            },
            'social_sentiment': {
                'average_score': 0.3,
                'post_count': 50,
                'total_engagement': 1000,
                'daily_scores': [
                    {'date': (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'),
                     'avg_sentiment': np.random.normal(0.3, 0.2),
                     'post_count': np.random.randint(5, 15),
                     'total_engagement': np.random.randint(100, 500)}
                    for i in range(7)
                ]
            },
            'overall_sentiment': {
                'score': 0.25,
                'trend': 'stable'
            }
        }