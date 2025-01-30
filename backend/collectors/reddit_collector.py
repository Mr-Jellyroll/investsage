import praw
import sqlite3
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
import re
from pathlib import Path
import os
import sys

# Add the project root to the Python path
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.append(str(project_root))

from python.utils.secrets import get_reddit_credentials
from python.collectors.sentiment_analyzer import SentimentAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedditCollector:
    def __init__(self, db_path=None):
        self.sentiment_analyzer = SentimentAnalyzer()
        
        # Handle database path
        if db_path:
            self.db_path = db_path
        else:
            # Use project root to construct default path
            project_root = Path(__file__).parent.parent.parent
            data_dir = project_root / 'data'
            # Create data directory if it doesn't exist
            data_dir.mkdir(exist_ok=True)
            self.db_path = str(data_dir / 'investsage.db')
            
        self.subreddits = [
            'wallstreetbets',
            'stocks',
            'investing',
            'stockmarket'
        ]
        
        try:
            credentials = get_reddit_credentials()
            logger.info("Successfully loaded Reddit credentials")
            
            # Initialize Reddit client
            self.reddit = praw.Reddit(
                client_id=credentials['client_id'],
                client_secret=credentials['client_secret'],
                user_agent=credentials['user_agent']
            )
            
            test_subreddit = self.reddit.subreddit('test')
            test_subreddit.description  # This will fail if auth is incorrect
            logger.info("Reddit authentication successful")
            
        except Exception as e:
            logger.error(f"Error initializing Reddit client: {str(e)}")
            raise

    def verify_database(self):
        """Verify database schema exists"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='social_sentiment'
                """)
                if not cursor.fetchone():
                    raise Exception("social_sentiment table not found in database")
                logger.info("Database schema verified")
                return True
        except Exception as e:
            logger.error(f"Database verification failed: {str(e)}")
            return False

    def extract_ticker_symbols(self, text: str) -> List[str]:
        """Extract stock symbols from text with better validation"""
        # Common false positives to filter out
        common_words = {
            'A', 'I', 'ME', 'MY', 'THE', 'AND', 'OR', 'IT', 'IS', 'BE', 'AI', 'CEO',
            'IPO', 'USA', 'GDP', 'NFL', 'CIA', 'FBI', 'SEC', 'ETF', 'ROI', 'YOLO',
            'IMO', 'FOMO', 'FUD', 'EPS', 'P/E', 'ATH', 'DD', 'PR', 'TV', 'UK',
            'ML', 'API', 'CEO', 'CPI', 'CTO', 'CFO', 'COO', 'PM', 'Q&A', 'M&A', 'FAANG',
            'R&D'
        }
        
        company_terms = {'INC', 'CORP', 'LTD', 'LLC', 'GROUP', 'HOLDINGS', 'PLC', 'CO', 'AG'}
        
        # Look for cashtags and standalone capitalized words
        potential_tickers = []
        
        cash_tags = re.findall(r'\$([A-Z]{1,5})\b', text)
        potential_tickers.extend(cash_tags)
        
        words = re.findall(r'\b[A-Z]{1,5}\b', text)
        potential_tickers.extend(words)
        
        # Clean and validate tickers
        valid_tickers = []
        for ticker in potential_tickers:
            ticker = ticker.strip('$')
            
            # Skip if it's in our blacklists
            if ticker in common_words or ticker in company_terms:
                continue
                
            # Skip single letters
            if len(ticker) < 2:
                continue
                
            # Must contain at least one letter
            if not any(c.isalpha() for c in ticker):
                continue
            
            valid_tickers.append(ticker)
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(valid_tickers))

    def calculate_sentiment(self, text: str) -> float:
        """Calculate sentiment score for text"""
        scores = self.sentiment_analyzer.analyze_text(text)
        return scores['compound']

    def count_engagements(self, post) -> int:
        """Count total engagements (score + comments)"""
        return post.score + post.num_comments

    def collect_subreddit_posts(self, subreddit_name: str, limit: int = 100) -> List[Dict]:
        """Collect posts from a subreddit"""
        try:
            logger.info(f"Collecting posts from r/{subreddit_name}")
            subreddit = self.reddit.subreddit(subreddit_name)
            posts = []

            for post in subreddit.hot(limit=limit):
                title_tickers = self.extract_ticker_symbols(getattr(post, 'title', ''))
                body_tickers = self.extract_ticker_symbols(getattr(post, 'selftext', ''))
                symbols = list(set(title_tickers + body_tickers))

                if symbols:  # Only process posts mentioning stocks
                    full_text = f"{getattr(post, 'title', '')}\n\n{getattr(post, 'selftext', '')}"
                    sentiment_score = self.calculate_sentiment(full_text)
                    engagement_count = self.count_engagements(post)
                    
                    for symbol in symbols:
                        post_data = {
                            'symbol': symbol,
                            'source': 'reddit',
                            'post_id': post.id,
                            'post_url': f"https://reddit.com{post.permalink}",
                            'content': full_text,
                            'posted_date': datetime.fromtimestamp(post.created_utc).isoformat(),
                            'sentiment_score': sentiment_score,
                            'engagement_count': engagement_count
                        }
                        posts.append(post_data)
                        logger.info(f"Found post mentioning {symbol} with {post_data['engagement_count']} engagements")

            return posts

        except Exception as e:
            logger.error(f"Error collecting posts from r/{subreddit_name}: {str(e)}")
            return []

    def save_posts(self, posts: List[Dict]):
        """Saves posts to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for post in posts:
                    try:
                        cursor.execute("""
                            INSERT OR IGNORE INTO social_sentiment
                            (symbol, source, post_id, post_url, content, 
                            posted_date, sentiment_score, engagement_count)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            post.get('symbol'),
                            post.get('source'),
                            post.get('post_id'),
                            post.get('post_url'),
                            post.get('content'),
                            post.get('posted_date'),
                            post.get('sentiment_score', 0.0),
                            post.get('engagement_count', 0)
                        ))
                        
                    except sqlite3.Error as e:
                        logger.error(f"Database error for post {post.get('post_id')}: {str(e)}")
                        logger.error(f"Post data: {post}")
                        continue
                
                conn.commit()
                logger.info(f"Successfully saved {len(posts)} posts to database")
                
        except Exception as e:
            logger.error(f"Error saving posts to database: {str(e)}")
            logger.error(f"First post data for debugging: {posts[0] if posts else 'No posts'}")
            raise

    def collect_sentiment(self, symbols: List[str] = None, post_limit: int = 100):
        """Collect social sentiment data"""
        logger.info("Starting social sentiment collection")
        
        # Verify database first
        if not self.verify_database():
            logger.error("Database verification failed. Please run setup_database.py first")
            return
        
        for subreddit in self.subreddits:
            posts = self.collect_subreddit_posts(subreddit, post_limit)
            
            # Filter by symbols if provided
            if symbols:
                posts = [p for p in posts if p['symbol'] in symbols]
            
            if posts:
                self.save_posts(posts)
                logger.info(f"Processed {len(posts)} posts from r/{subreddit}")
            
        logger.info("Social sentiment collection completed")

if __name__ == "__main__":
    try:
        # Example usage
        collector = RedditCollector()
        logger.info(f"Using database at: {collector.db_path}")
        collector.collect_sentiment(['AAPL', 'MSFT', 'GOOGL'])
    except Exception as e:
        logger.error(f"Error running collector: {str(e)}")
        raise