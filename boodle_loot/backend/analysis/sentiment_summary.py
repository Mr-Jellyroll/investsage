import sqlite3
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_sentiment(symbol: str = None, days: int = 7):
    """Analyze sentiment for a symbol or all symbols"""
    try:
        # Get database path
        DB_PATH = Path(__file__).parent.parent.parent / 'data' / 'investsage.db'
        logger.info(f"Using database at: {DB_PATH}")
        
        conn = sqlite3.connect(str(DB_PATH))
        
        # Build query
        query = """
            SELECT 
                ss.symbol,
                COALESCE(s.company_name, ss.symbol) as company_name,
                COUNT(*) as mention_count,
                ROUND(AVG(ss.sentiment_score), 2) as avg_sentiment,
                SUM(ss.engagement_count) as total_engagement,
                COUNT(CASE WHEN ss.sentiment_score > 0.05 THEN 1 END) as bullish_count,
                COUNT(CASE WHEN ss.sentiment_score < -0.05 THEN 1 END) as bearish_count,
                COUNT(CASE WHEN ss.sentiment_score BETWEEN -0.05 AND 0.05 THEN 1 END) as neutral_count,
                MAX(ss.posted_date) as latest_post
            FROM social_sentiment ss
            LEFT JOIN stocks s ON ss.symbol = s.symbol
            WHERE ss.posted_date >= datetime('now', ?)
        """
        
        params = [f'-{days} days']
        if symbol:
            query += " AND ss.symbol = ?"
            params.append(symbol.upper())
        
        query += " GROUP BY ss.symbol, COALESCE(s.company_name, ss.symbol) ORDER BY mention_count DESC"
        
        # Execute query
        df = pd.read_sql_query(query, conn, params=params)
        
        if df.empty:
            print("\nNo sentiment data found for the specified criteria.")
            return
        
        # Print results
        print("\nSentiment Analysis Summary")
        print("=" * 80)
        print(f"Period: Last {days} days")
        print(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        for _, row in df.iterrows():
            print(f"\nSymbol: {row['symbol']} ({row['company_name']})")
            print(f"Total Mentions: {row['mention_count']}")
            print(f"Sentiment Score: {row['avg_sentiment']:.2f}")
            
            # Calculate sentiment distribution
            total = row['bullish_count'] + row['bearish_count'] + row['neutral_count']
            print("\nSentiment Distribution:")
            print(f"  - Bullish: {row['bullish_count']} posts ({(row['bullish_count']/total*100):.1f}%)")
            print(f"  - Bearish: {row['bearish_count']} posts ({(row['bearish_count']/total*100):.1f}%)")
            print(f"  - Neutral: {row['neutral_count']} posts ({(row['neutral_count']/total*100):.1f}%)")
            
            print(f"\nEngagement:")
            print(f"  - Total Engagement: {row['total_engagement']:,}")
            print(f"  - Avg Engagement per Post: {(row['total_engagement']/row['mention_count']):.1f}")
            print(f"Latest Post: {row['latest_post']}")
            print("-" * 80)
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {str(e)}")
        raise

def main():
    """Main function to run sentiment analysis"""
    print("\nReddit Sentiment Analysis Tool")
    print("=" * 50)
    print("1. Analyze all symbols")
    print("2. Analyze specific symbol")
    print("3. Change time period")
    
    choice = input("\nEnter your choice (1-3): ")
    
    if choice == '1':
        analyze_sentiment()
    elif choice == '2':
        symbol = input("Enter symbol (e.g., AAPL): ").upper()
        analyze_sentiment(symbol)
    elif choice == '3':
        days = int(input("Enter number of days to analyze: "))
        analyze_sentiment(days=days)
    else:
        print("Invalid choice!")

if __name__ == "__main__":
    main()