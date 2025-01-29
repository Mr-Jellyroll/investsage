import { NextResponse } from 'next/server';
import { getDatabase } from '@/lib/database/sqlite';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const symbol = searchParams.get('symbol');
  
  if (!symbol) {
    return NextResponse.json(
      { error: 'Symbol parameter is required' },
      { status: 400 }
    );
  }
  
  try {
    const db = await getDatabase();
    
    // Fetch basic stock info
    const stockInfo = await db.get(
      'SELECT * FROM stocks WHERE symbol = ?',
      [symbol.toUpperCase()]
    );
    
    if (!stockInfo) {
      return NextResponse.json(
        { error: 'Stock not found' },
        { status: 404 }
      );
    }
    
    // Fetch latest 30 days of historical data
    const historicalPrices = await db.all(`
      SELECT date, open, high, low, close, volume
      FROM historical_prices
      WHERE symbol = ?
      ORDER BY date DESC
      LIMIT 30
    `, [symbol.toUpperCase()]);
    
    return NextResponse.json({
      basicInfo: stockInfo,
      historicalPrices: historicalPrices
    });
    
  } catch (error) {
    console.error('Database error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function POST(request: Request) {
  try {
    const { symbol } = await request.json();
    
    if (!symbol) {
      return NextResponse.json(
        { error: 'Symbol is required' },
        { status: 400 }
      );
    }
    
    // Trigger Python data collector
    const { spawn } = require('child_process');
    const collector = spawn('python', [
      'python/collectors/yahoo_finance.py',
      symbol.toUpperCase()
    ]);
    
    return new Promise((resolve) => {
      collector.on('close', (code) => {
        if (code === 0) {
          resolve(NextResponse.json({ 
            message: 'Data collection initiated' 
          }));
        } else {
          resolve(NextResponse.json(
            { error: 'Data collection failed' },
            { status: 500 }
          ));
        }
      });
    });
    
  } catch (error) {
    console.error('Error processing request:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}