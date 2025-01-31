export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  async fetchStockData(symbol: string) {
    try {
      const stockResponse = await fetch(`${this.baseUrl}/stock/${symbol}`);
      if (!stockResponse.ok) {
        const errorData = await stockResponse.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to fetch stock data');
      }
      const stockData = await stockResponse.json();

      const analysisRequest = {
        symbol,
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
        throw new Error(errorData.detail || 'Failed to fetch analysis data');
      }

      const analysisData = await analysisResponse.json();
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
      console.log(`Searching for symbols matching: ${query}`);
      const response = await fetch(
        `${this.baseUrl}/stock/search?q=${encodeURIComponent(query)}`
      );
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to search symbols');
      }
      
      const data = await response.json();
      console.log('Search results:', data);
      return data;
    } catch (error) {
      console.error('Error searching symbols:', error);
      throw error;
    }
  }
}