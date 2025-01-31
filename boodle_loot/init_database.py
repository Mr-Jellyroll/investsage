import sqlite3
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_database(db_path: str):
    """Initialize database with test data"""
    # Convert to Path object
    db_path = Path(db_path)
    
    # Create parent directories if they don't exist
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Initializing database at {db_path}")
    
    # First run setup_database.py to create tables
    from setup_database import reset_database
    reset_database()
    
    # Test symbols
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META']
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Initialize stocks table
        for symbol in symbols:
            logger.info(f"Fetching data for {symbol}")
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            cursor.execute("""
                INSERT OR REPLACE INTO stocks 
                (symbol, company_name, sector, industry)
                VALUES (?, ?, ?, ?)
            """, (
                symbol,
                info.get('longName', ''),
                info.get('sector', ''),
                info.get('industry', '')
            ))
            
            # Get historical data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            hist = ticker.history(start=start_date, end=end_date)
            
            # Save historical prices
            for index, row in hist.iterrows():
                cursor.execute("""
                    INSERT OR REPLACE INTO historical_prices
                    (symbol, date, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    symbol,
                    index.strftime('%Y-%m-%d'),
                    row['Open'],
                    row['High'],
                    row['Low'],
                    row['Close'],
                    row['Volume']
                ))
            
            logger.info(f"Added data for {symbol}")
        
        conn.commit()
        logger.info("Database initialization complete")
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    # Get the absolute path to the data directory
    db_path = Path(__file__).parent.parent / 'data' / 'investsage.db'
    initialize_database(str(db_path))