import sys
from pathlib import Path
import logging
from datetime import datetime

current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

from collectors.edgar_collector import EDGARCollector

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DB_PATH = parent_dir.parent / 'data' / 'investsage.db'

def test_edgar():
    print(f"Using database at: {DB_PATH}")
    
    # Initialize
    collector = EDGARCollector(str(DB_PATH))
    
    # Test collection
    symbol = "AAPL"
    print(f"\nTesting EDGAR collection for {symbol}")
    
    # Test CIK lookup
    cik = collector.get_company_cik(symbol)
    print(f"CIK number: {cik}")
    
    # Test filing
    collector.collect_filings(symbol, filing_types=['10-K', '10-Q'])
    
    # Verify entries
    import sqlite3
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    print("\nSEC Filings in database:")
    cursor.execute("""
        SELECT filing_type, filing_date, filing_url, description 
        FROM sec_filings 
        WHERE symbol = ? 
        ORDER BY filing_date DESC 
        LIMIT 5
    """, (symbol,))
    
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            print(f"\nType: {row[0]}")
            print(f"Date: {row[1]}")
            print(f"URL: {row[2]}")
            print(f"Description: {row[3]}")
            print("-" * 80)
    else:
        print("No filings found in database")
    
    # Get some stats
    cursor.execute("""
        SELECT filing_type, COUNT(*) 
        FROM sec_filings 
        WHERE symbol = ? 
        GROUP BY filing_type
    """, (symbol,))
    
    stats = cursor.fetchall()
    if stats:
        print("\nFiling Statistics:")
        for stat in stats:
            print(f"{stat[0]}: {stat[1]} filings")
    
    conn.close()

if __name__ == "__main__":
    test_edgar()