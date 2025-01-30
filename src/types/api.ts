export type AnalysisType = 'technical' | 'sentiment' | 'ml' | 'options' | 'portfolio' | 'risk' | 'all';

export interface StockData {
  date: string;
  price: number;
  volume: number;
  rsi?: number;
  macd?: number;
  signal?: number;
  upperBand?: number;
  lowerBand?: number;
}

export interface TechnicalIndicators {
  sma20: number;
  sma50: number;
  rsi: number;
  macd: {
    macd: number;
    signal: number;
    histogram: number;
  };
  bollingerBands: {
    upper: number;
    middle: number;
    lower: number;
  };
}