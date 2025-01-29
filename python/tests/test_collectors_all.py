import sys
import os
import logging
from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / 'data'
DB_PATH = DATA_DIR / 'investsage.db'
DATA_DIR.mkdir(exist_ok=True)

sys.path.append(str(Path(__file__).parent.parent))

from collectors.yahoo_finance import StockDataCollector
from collectors.news_collector import NewsCollector
from collectors.edgar_collector import EDGARCollector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_stock_collector():
    """Test basic stock data collection"""
    logger.info("Testing stock data collector...")
    collector = StockDataCollector(str(DB_PATH))
    success = collector.update_stock_data("AAPL")
    assert success, "Stock data collection failed"
    logger.info("Stock data collection successful")

def test_news_collector():
    """Test news collection"""
    logger.info("Testing news collector...")
    collector = NewsCollector(str(DB_PATH))
    collector.rss_feeds = {
        'yahoo_finance': 'https://finance.yahoo.com/news/rssindex',
        'seeking_alpha': 'https://seekingalpha.com/market_currents.xml'
    }
    collector.collect_news()
    logger.info("News collection completed")

def test_edgar_collector():
    """Test SEC filing collection"""
    logger.info("Testing EDGAR collector...")
    collector = EDGARCollector(str(DB_PATH))
    collector.collect_filings("AAPL", filing_types=['10-K', '10-Q'])
    logger.info("EDGAR collection completed")

def verify_database():
    """Check if data was properly saved"""
    logger.info("Verifying database...")
    logger.info(f"Using database at: {DB_PATH}")
    
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # Check stocks table
        cursor.execute("SELECT COUNT(*) FROM stocks")
        stock_count = cursor.fetchone()[0]
        logger.info(f"Number of stocks in database: {stock_count}")
        
        # Check historical prices
        cursor.execute("SELECT COUNT(*) FROM historical_prices")
        price_count = cursor.fetchone()[0]
        logger.info(f"Number of price records: {price_count}")
        
        # Check news articles
        cursor.execute("SELECT COUNT(*) FROM news_articles")
        news_count = cursor.fetchone()[0]
        logger.info(f"Number of news articles: {news_count}")
        
        # Check SEC filings
        cursor.execute("SELECT COUNT(*) FROM sec_filings")
        filing_count = cursor.fetchone()[0]
        logger.info(f"Number of SEC filings: {filing_count}")
        
        # Show some sample data
        print("\nSample Stock Data:")
        cursor.execute("SELECT * FROM stocks LIMIT 1")
        print(cursor.fetchone())
        
        print("\nSample Historical Prices:")
        cursor.execute("SELECT * FROM historical_prices LIMIT 1")
        print(cursor.fetchone())
        
        print("\nSample News Articles:")
        cursor.execute("SELECT symbol, title, published_date FROM news_articles LIMIT 1")
        print(cursor.fetchone())
        
        print("\nSample SEC Filings:")
        cursor.execute("SELECT symbol, filing_type, filing_date FROM sec_filings LIMIT 1")
        print(cursor.fetchone())
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Database verification failed: {str(e)}")

def init_database():
    """Initialize the database with required tables"""
    try:
        logger.info(f"Initializing database at: {DB_PATH}")
        
        conn = sqlite3.connect(str(DB_PATH))
        conn.executescript('''
            -- Basic stock information
            CREATE TABLE IF NOT EXISTS stocks (
                symbol TEXT PRIMARY KEY,
                company_name TEXT NOT NULL,
                sector TEXT,
                industry TEXT,
                description TEXT,
                website TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Historical price data
            CREATE TABLE IF NOT EXISTS historical_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                date TEXT NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume INTEGER NOT NULL,
                FOREIGN KEY (symbol) REFERENCES stocks(symbol),
                UNIQUE(symbol, date)
            );

            -- News articles
            CREATE TABLE IF NOT EXISTS news_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                title TEXT NOT NULL,
                source TEXT NOT NULL,
                url TEXT NOT NULL,
                published_date TIMESTAMP NOT NULL,
                summary TEXT,
                sentiment_score REAL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol) REFERENCES stocks(symbol),
                UNIQUE(url)
            );

            -- SEC filings
            CREATE TABLE IF NOT EXISTS sec_filings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                filing_type TEXT NOT NULL,
                filing_date TIMESTAMP NOT NULL,
                filing_url TEXT NOT NULL,
                description TEXT,
                extracted_text TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol) REFERENCES stocks(symbol),
                UNIQUE(filing_url)
            );
        ''')
        conn.close()
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        # Initialize
        init_database()
        
        # Test each collector
        test_stock_collector()
        test_news_collector()
        test_edgar_collector()
        
        verify_database()
        
    except Exception as e:
        logger.error(f"Testing failed: {str(e)}")
        raise