
export enum AnalysisType {
    TECHNICAL = 'technical',
    SENTIMENT = 'sentiment',
    ML = 'ml',
    OPTIONS = 'options',
    PORTFOLIO = 'portfolio',
    RISK = 'risk',
    ALL = 'all',
  }
  
  export interface AnalysisMetadata {
    timestamp: string;
    symbol: string;
    analysisType: AnalysisType;
  }
  
  export interface TechnicalAnalysis {
    trendIndicators: {
      sma20: number;
      sma50: number;
      rsi: number;
      macd: {
        line: number;
        signal: number;
        histogram: number;
      };
    };
    volatilityIndicators: {
      bollingerBands: {
        upper: number;
        middle: number;
        lower: number;
      };
      atr: number;
    };
    volumeIndicators: {
      obv: number;
      vwap: number;
    };
  }
  
  export interface SentimentAnalysis {
    news: {
      sentiment: number;
      articleCount: number;
    };
    social: {
      sentiment: number;
      engagement: number;
      postCount: number;
    };
  }
  
  export interface MLPrediction {
    predictions: number[];
    confidence: number;
    importantFeatures: Record<string, number>;
  }
  
  export interface RiskAnalysis {
    volatility: number;
    var: number;
    beta: number;
    sharpeRatio: number;
    maxDrawdown: number;
  }
  
  export interface AnalysisResult {
    technical?: TechnicalAnalysis;
    sentiment?: SentimentAnalysis;
    mlPredictions?: MLPrediction;
    risk?: RiskAnalysis;
  }