import { AnalysisType, StockData, TechnicalIndicators } from '@/types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api';

export class ApiClient {
  async fetchStockData(symbol: string): Promise<StockData[]> {
    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        symbol,
        analysisType: 'technical',
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch stock data');
    }

    const data = await response.json();
    return data.data?.stockData || [];
  }

  async fetchTechnicalIndicators(symbol: string): Promise<TechnicalIndicators> {
    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        symbol,
        analysisType: 'technical',
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch technical indicators');
    }

    const data = await response.json();
    return data.data?.indicators || {};
  }

  async searchSymbols(query: string): Promise<string[]> {
    const response = await fetch(`${API_BASE_URL}/symbols?search=${query}`);
    
    if (!response.ok) {
      throw new Error('Failed to search symbols');
    }

    return response.json();
  }
}