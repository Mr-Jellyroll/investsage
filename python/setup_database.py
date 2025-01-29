import sqlite3
from pathlib import Path

def reset_database():
    # Get path to database
    DB_PATH = Path(__file__).parent.parent / 'data' / 'investsage.db'
    print(f"Resetting database at: {DB_PATH}")

    # Remove existing database if it exists
    if DB_PATH.exists():
        DB_PATH.unlink()

    # Create new database
    conn = sqlite3.connect(str(DB_PATH))
    conn.executescript('''
        -- SEC filings
        CREATE TABLE IF NOT EXISTS sec_filings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            filing_type TEXT NOT NULL,
            filing_date TEXT NOT NULL,
            filing_url TEXT NOT NULL,
            description TEXT,
            extracted_text TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (symbol) REFERENCES stocks(symbol),
            UNIQUE(filing_url)
        );
        
        -- Add other tables back here...
    ''')
    conn.close()
    print("Database reset complete")

if __name__ == "__main__":
    reset_database()