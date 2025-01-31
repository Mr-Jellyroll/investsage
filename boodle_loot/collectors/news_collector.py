import feedparser
import sqlite3
import logging
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
DB_PATH = DATA_DIR / 'investsage.db'

# Create data dir if it doesn't exist
DATA_DIR.mkdir(exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsCollector:
    def __init__(self, db_path='./data/investsage.db'):
        self.db_path = db_path
        self.rss_feeds = {
            'yahoo_finance': 'https://finance.yahoo.com/rss/',
            'seeking_alpha': 'https://seekingalpha.com/feed',
            'marketwatch': 'http://feeds.marketwatch.com/marketwatch/topstories/'
        }
        
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def extract_ticker_symbols(self, text: str) -> List[str]:
        """
        Looks for capitalized words 1-5 chars long
        """
        import re
        potential_tickers = re.findall(r'\b[A-Z]{1,5}\b', text)

        # Filter out common words that might be mistaken for tickers
        common_words = {'A', 'I', 'AT', 'BE', 'DO', 'IT', 'SO', 'GO', 'THE'}
        return [t for t in potential_tickers if t not in common_words]
    
    def fetch_article_content(self, url: str) -> str:
        """
        Fetches main content from an article
        """
        try:
            headers = {
                'User-Agent': 'InvestSage Research Bot (Open Source Project)'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(['script', 'style']):
                script.decompose()
            
            # Extract text from article body
            article_body = soup.find('article') or soup.find(class_='article-body')
            if article_body:
                return article_body.get_text(separator=' ', strip=True)
            
            main_content = soup.find('main') or soup.find(id='content')
            if main_content:
                return main_content.get_text(separator=' ', strip=True)
            
            return soup.get_text(separator=' ', strip=True)
            
        except Exception as e:
            logger.error(f"Error fetching article content from {url}: {str(e)}")
            return ""
    
    def calculate_sentiment(self, text: str) -> float:
        """
        Placeholder for sentiment analysis
        """
        return 0.0
    
    def parse_feed(self, feed_url: str) -> List[Dict]:
        """
        Parses an RSS feed
        """
        try:
            feed = feedparser.parse(feed_url)
            articles = []
            
            for entry in feed.entries:
                # Get description
                description = (
                    getattr(entry, 'description', '') or 
                    getattr(entry, 'summary', '') or 
                    getattr(entry, 'content', [{'value': ''}])[0]['value']
                )
                
                # Get title
                title = getattr(entry, 'title', '')
                
                # Extract symbols
                title_symbols = self.extract_ticker_symbols(title)
                desc_symbols = self.extract_ticker_symbols(description)
                symbols = list(set(title_symbols + desc_symbols))
                
                if symbols:
                    try:
                        published_date = datetime(*entry.published_parsed[:6]).isoformat()
                    except (AttributeError, TypeError):
                        # Try other date fields
                        published_date = (
                            getattr(entry, 'updated', '') or 
                            getattr(entry, 'published', '') or 
                            datetime.now().isoformat()
                        )
                    
                    article = {
                        'title': title,
                        'url': entry.link,
                        'published_date': published_date,
                        'summary': description,
                        'symbols': symbols,
                        'source': feed_url.split('/')[2]
                    }
                    articles.append(article)
                    
                    time.sleep(1)
            
            return articles
            
        except Exception as e:
            logger.error(f"Error parsing feed {feed_url}: {str(e)}")
            return []
    
    def save_articles(self, articles: List[Dict]):
        """
        Saves articles to the database
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                for article in articles:
                    for symbol in article['symbols']:
                        try:
                            cursor.execute("""
                                INSERT OR IGNORE INTO news_articles
                                (symbol, title, source, url, published_date, summary, sentiment_score)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            """, (
                                symbol,
                                article['title'],
                                article['source'],
                                article['url'],
                                article['published_date'],
                                article['summary'],
                                self.calculate_sentiment(article['summary'])
                            ))
                        except sqlite3.Error as e:
                            logger.error(f"Error saving article {article['url']} for symbol {symbol}: {str(e)}")
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error in save_articles: {str(e)}")
    
    def collect_news(self):
        """
        Main method to collect news from all sources
        """
        logger.info("Starting news collection")
        
        for source, feed_url in self.rss_feeds.items():
            logger.info(f"Processing feed: {source}")
            articles = self.parse_feed(feed_url)
            if articles:
                self.save_articles(articles)
                logger.info(f"Saved {len(articles)} articles from {source}")
            
            # Be nice to servers
            time.sleep(2)
        
        logger.info("News collection completed")

def __init__(self, db_path=None):
    self.db_path = str(db_path or DB_PATH)

if __name__ == "__main__":
    collector = NewsCollector()
    collector.collect_news()