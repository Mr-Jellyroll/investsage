import { AnalysisRequest } from '@/types/api';

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl = '/api') {
    this.baseUrl = baseUrl;
  }

  async fetchStockData(symbol: string) {
    try {
      // First get basic stock info
      const stockResponse = await fetch(`${this.baseUrl}/stock/${symbol}`);
      if (!stockResponse.ok) {
        throw new Error('Failed to fetch stock data');
      }
      const stockData = await stockResponse.json();

      // Then get analysis data
      const analysisRequest: AnalysisRequest = {
        symbol,
        analysisType: 'all'
      };

      const analysisResponse = await fetch(`${this.baseUrl}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(analysisRequest),
      });

      if (!analysisResponse.ok) {
        throw new Error('Failed to fetch analysis data');
      }

      const analysisData = await analysisResponse.json();

      // Combine the data
      return {
        ...stockData,
        ...analysisData.data
      };
    } catch (error) {
      console.error('Error fetching data:', error);
      throw error;
    }
  }

  async searchSymbols(query: string): Promise<string[]> {
    try {
      const response = await fetch(`${this.baseUrl}/stock/search?q=${encodeURIComponent(query)}`);
      if (!response.ok) {
        throw new Error('Failed to search symbols');
      }
      return await response.json();
    } catch (error) {
      console.error('Error searching symbols:', error);
      throw error;
    }
  }
}