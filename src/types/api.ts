
export type AnalysisType = 
  | 'technical'
  | 'sentiment'
  | 'ml'
  | 'options'
  | 'portfolio'
  | 'risk'
  | 'all';

export interface AnalysisRequest {
  symbol: string;
  analysisType: AnalysisType;
  startDate?: string;
  endDate?: string;
  params?: Record<string, unknown>;
}

export interface AnalysisResponse {
  success: boolean;
  data?: {
    technical?: TechnicalAnalysis;
    sentiment?: SentimentAnalysis;
    ml?: MLAnalysis;
    options?: OptionsAnalysis;
    portfolio?: PortfolioAnalysis;
    risk?: RiskAnalysis;
  };
  error?: string;
  warnings?: string[];
  metadata?: Record<string, unknown>;
}

export interface TechnicalAnalysis {
  trend_indicators: {
    moving_averages: Array<{
      date: string;
      sma20: number;
      sma50: number;
      ema12: number;
      ema26: number;
    }>;
    macd: {
      macd_line: number;
      signal_line: number;
      histogram: number;
    };
    adx: number;
    trend_strength: number;
    trend_direction: string;
  };
  momentum_indicators: {
    rsi: number;
    stochastic: {
      k: number;
      d: number;
    };
  };
  volatility_indicators: {
    bollinger_bands: {
      upper: number;
      middle: number;
      lower: number;
    };
  };
}

// Add other analysis type interfaces here...