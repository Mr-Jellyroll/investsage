import sys
from pathlib import Path

current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

from collectors.news_collector import NewsCollector
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = parent_dir.parent / 'data' / 'investsage.db'
print(f"Using database at: {DB_PATH}")

# Initialize collector
collector = NewsCollector(str(DB_PATH))
collector.rss_feeds = {
    'yahoo_finance': 'https://finance.yahoo.com/news/rssindex',
    'seeking_alpha': 'https://seekingalpha.com/market_currents.xml',
    'marketwatch': 'http://feeds.marketwatch.com/marketwatch/topstories/'
}

# Test
collector.collect_news()

# Verify
import sqlite3
conn = sqlite3.connect(str(DB_PATH))
cursor = conn.cursor()

print("\nNews articles:")
cursor.execute("SELECT symbol, title, source, published_date FROM news_articles LIMIT 5")
print(cursor.fetchall())

conn.close()