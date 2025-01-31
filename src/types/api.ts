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
  analysis_type: AnalysisType;
  start_date?: string;
  end_date?: string;
  params?: Record<string, unknown>;
}

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl = 'http://localhost:8000') {
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
        symbol: symbol,
        analysis_type: 'all'
      };

      const analysisResponse = await fetch(`${this.baseUrl}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(analysisRequest),
      });

      if (!analysisResponse.ok) {
        const errorData = await analysisResponse.json().catch(() => ({}));
        console.error('Analysis response error:', errorData);
        throw new Error(errorData.detail || 'Failed to fetch analysis data');
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
      const response = await fetch(
        `${this.baseUrl}/stock/search?q=${encodeURIComponent(query)}`
      );
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to search symbols');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error searching symbols:', error);
      throw error;
    }
  }
}