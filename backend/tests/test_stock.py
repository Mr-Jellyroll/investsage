import sys
import os
from pathlib import Path

current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

from collectors.yahoo_finance import StockDataCollector

DB_PATH = parent_dir.parent / 'data' / 'investsage.db'
print(f"Using database at: {DB_PATH}")

collector = StockDataCollector(str(DB_PATH))
success = collector.update_stock_data("AAPL")
print(f"Collection {'succeeded' if success else 'failed'}")

# Verify data
import sqlite3
conn = sqlite3.connect(str(DB_PATH))
cursor = conn.cursor()

print("\nStocks table:")
cursor.execute("SELECT * FROM stocks")
print(cursor.fetchall())

print("\nHistorical prices:")
cursor.execute("SELECT * FROM historical_prices LIMIT 5")
print(cursor.fetchall())

conn.close()