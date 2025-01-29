export interface StockData {
    symbol: string;
    companyName: string;
    currentPrice: number;
    change: number;
    changePercent: number;
    marketCap: number;
    volume: number;
    peRatio?: number;
  }
  
  export interface HistoricalPrice {
    date: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
  }