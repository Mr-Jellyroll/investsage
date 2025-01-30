import sqlite3
from pathlib import Path

def reset_database():
    
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
        
        -- Social sentiment data
        CREATE TABLE IF NOT EXISTS social_sentiment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            source TEXT NOT NULL,
            post_id TEXT NOT NULL,
            post_url TEXT,
            content TEXT,
            posted_date TIMESTAMP NOT NULL,
            sentiment_score REAL,
            engagement_count INTEGER,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (symbol) REFERENCES stocks(symbol),
            UNIQUE(source, post_id)
        );
    ''')
    conn.close()
    print("Database reset complete")

if __name__ == "__main__":
    reset_database()