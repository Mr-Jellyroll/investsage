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
    CREATE TABLE IF NOT EXISTS stocks (
      symbol TEXT PRIMARY KEY,
      company_name TEXT NOT NULL,
      last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

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
  `);
}