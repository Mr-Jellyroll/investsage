
import praw
import sqlite3
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
import re
from pathlib import Path
from utils.secrets import get_reddit_credentials
from .sentiment_analyzer import SentimentAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedditCollector:
    def __init__(self, db_path='./data/investsage.db'):
        self.sentiment_analyzer = SentimentAnalyzer()
        self.db_path = db_path
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
        
        # First, find potential tickers
        # Look for:
        # 1. Words starting with $ followed by letters
        # 2. Standalone capitalized words 1-5 letters long
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
        return scores['compound']  # Return compound score

    def count_engagements(self, post) -> int:
        """
        Count total engagements (score + comments)
        """
        return post.score + post.num_comments

    def collect_subreddit_posts(self, subreddit_name: str, limit: int = 100) -> List[Dict]:

        try:
            logger.info(f"Collecting posts from r/{subreddit_name}")
            subreddit = self.reddit.subreddit(subreddit_name)
            posts = []

            # Get hot posts
            for post in subreddit.hot(limit=limit):

                title_tickers = self.extract_ticker_symbols(post.title)
                body_tickers = self.extract_ticker_symbols(post.selftext)
                symbols = list(set(title_tickers + body_tickers))

                if symbols:  # Only process posts mentioning stocks
                    for symbol in symbols:
                        post_data = {
                            'symbol': symbol,
                            'source': 'reddit',
                            'post_id': post.id,
                            'post_url': f"https://reddit.com{post.permalink}",
                            'content': f"{post.title}\n\n{post.selftext}",
                            'posted_date': datetime.fromtimestamp(post.created_utc).isoformat(),
                            'sentiment_score': self.calculate_sentiment(f"{post.title} {post.selftext}"),
                            'engagement_count': self.count_engagements(post)
                        }
                        posts.append(post_data)
                        logger.info(f"Found post mentioning {symbol} with {post_data['engagement_count']} engagements")

            return posts

        except Exception as e:
            logger.error(f"Error collecting posts from r/{subreddit_name}: {str(e)}")
            return []

    def save_posts(self, posts: List[Dict]):
        """Save posts to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for post in posts:
                    cursor.execute("""
                        INSERT OR IGNORE INTO social_sentiment
                        (symbol, source, post_id, post_url, content, 
                         posted_date, sentiment_score, engagement_count)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        post['symbol'],
                        post['source'],
                        post['post_id'],
                        post['post_url'],
                        post['content'],
                        post['posted_date'],
                        post['sentiment_score'],
                        post['engagement_count']
                    ))
                
                conn.commit()
                logger.info(f"Saved {len(posts)} posts to database")
                
        except Exception as e:
            logger.error(f"Error saving posts to database: {str(e)}")

    def collect_sentiment(self, symbols: List[str] = None, post_limit: int = 100):
        """
        Main method to collect social sentiment data
        """
        logger.info("Starting social sentiment collection")
        
        for subreddit in self.subreddits:
            posts = self.collect_subreddit_posts(subreddit, post_limit)
            
            # Filter by symbols
            if symbols:
                posts = [p for p in posts if p['symbol'] in symbols]
            
            if posts:
                self.save_posts(posts)
                logger.info(f"Processed {len(posts)} posts from r/{subreddit}")
            
        logger.info("Social sentiment collection completed")

if __name__ == "__main__":
    # Example usage
    collector = RedditCollector()
    collector.collect_sentiment(['AAPL', 'MSFT', 'GOOGL'])