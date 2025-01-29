import { Database } from 'sqlite3';
import { open } from 'sqlite';

let db: Database | null = null;

export async function getDatabase() {
  if (!db) {
    db = await open({
      filename: './data/investsage.db',
      driver: Database
    });

    await initializeTables();
  }
  return db;
}

async function initializeTables() {
  const db = await getDatabase();

  await db.exec(`
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

    -- Social sentiment
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

    -- Financial metrics
    CREATE TABLE IF NOT EXISTS financial_metrics (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      symbol TEXT NOT NULL,
      metric_name TEXT NOT NULL,
      metric_value REAL NOT NULL,
      period_end_date TEXT NOT NULL,
      period_type TEXT NOT NULL,
      last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (symbol) REFERENCES stocks(symbol),
      UNIQUE(symbol, metric_name, period_end_date, period_type)
    );
  `);
}