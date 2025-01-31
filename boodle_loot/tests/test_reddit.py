import sys
from pathlib import Path
import logging

current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

from collectors.reddit_collector import RedditCollector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = parent_dir.parent / 'data' / 'investsage.db'

def test_reddit():
    print(f"Using database at: {DB_PATH}")
    
    collector = RedditCollector(str(DB_PATH))
    
    # Test collection
    symbols = ['AAPL', 'MSFT', 'GOOGL']
    collector.collect_sentiment(symbols, post_limit=50)
    
    # Verify data
    import sqlite3
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    print("\nReddit sentiment data in database:")
    cursor.execute("""
        SELECT symbol, COUNT(*) as post_count, 
               AVG(sentiment_score) as avg_sentiment,
               SUM(engagement_count) as total_engagement
        FROM social_sentiment
        WHERE source = 'reddit'
        GROUP BY symbol
        ORDER BY total_engagement DESC
    """)
    
    rows = cursor.fetchall()
    if rows:
        print("\nSymbol | Posts | Avg Sentiment | Total Engagement")
        print("-" * 50)
        for row in rows:
            print(f"{row[0]:<6} | {row[1]:>5} | {row[2]:>12.2f} | {row[3]:>15}")
    else:
        print("No sentiment data found")
    
    conn.close()

if __name__ == "__main__":
    test_reddit()