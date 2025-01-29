import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import sqlite3
import logging
import os
from pathlib import Path

# Get absolute path
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
DB_PATH = DATA_DIR / 'investsage.db'

# Create data dir if it doesn't exist
DATA_DIR.mkdir(exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockDataCollector:
    def __init__(self, db_path='./data/investsage.db'):
        self.db_path = db_path

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def fetch_basic_info(self, symbol: str):
        """
        Fetches basic company info
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            return {
                'symbol': symbol,
                'company_name': info.get('longName', ''),
                'current_price': info.get('currentPrice', 0),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('forwardPE', None),
                'volume': info.get('volume', 0),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', '')
            }
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def fetch_historical_data(self, symbol: str, days: int = 365):
        """
        Fetches historical price data
        """
        try:
            ticker = yf.Ticker(symbol)
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            df = ticker.history(start=start_date)
            
            if df.empty:
                return None
                
            df = df.reset_index()
            df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
            df = df.rename(columns={
                'Date': 'date',
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            
            return df.to_dict('records')
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
            return None
    
    def save_basic_info(self, data: dict):
        """
        Basic company info
        """
        if not data:
            return False
            
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO stocks 
                    (symbol, company_name, sector, industry, last_updated)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    data['symbol'],
                    data['company_name'],
                    data.get('sector', ''),
                    data.get('industry', '')
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving basic info: {str(e)}")
            return False
    
    def save_historical_data(self, symbol: str, data: list):
        """
        Saves historical price
        """
        if not data:
            return False
            
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                for record in data:
                    cursor.execute("""
                        INSERT OR REPLACE INTO historical_prices
                        (symbol, date, open, high, low, close, volume)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        symbol,
                        record['date'],
                        record['open'],
                        record['high'],
                        record['low'],
                        record['close'],
                        record['volume']
                    ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving historical data: {str(e)}")
            return False

    def update_stock_data(self, symbol: str):
        """
        Updates basic info and historical data
        """
        logger.info(f"Updating data for {symbol}")
        
        # Fetch and save basic info
        basic_info = self.fetch_basic_info(symbol)
        if basic_info:
            self.save_basic_info(basic_info)
            logger.info(f"Updated basic info for {symbol}")
        
        # Fetch and save historical data
        historical_data = self.fetch_historical_data(symbol)
        if historical_data:
            self.save_historical_data(symbol, historical_data)
            logger.info(f"Updated historical data for {symbol}")
        
        return basic_info is not None and historical_data is not None

def __init__(self, db_path=None):
    self.db_path = str(db_path or DB_PATH)

if __name__ == "__main__":
    # Example
    collector = StockDataCollector()
    collector.update_stock_data("AAPL")