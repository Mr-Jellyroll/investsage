// Mock data for development
const MOCK_SYMBOLS = [
  'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META', 'TSLA', 'NVDA', 'JPM', 'BAC', 'WMT'
];

const MOCK_STOCK_DATA = {
  AAPL: {
    price: 185.92,
    change: 2.34,
    changePercent: 1.27,
    volume: 58432100,
    previousClose: 183.58,
    historicalData: [
      { date: '2024-01-01', price: 180.50, volume: 1200000 },
      { date: '2024-01-02', price: 182.75, volume: 1500000 },
      { date: '2024-01-03', price: 181.25, volume: 1100000 },
      { date: '2024-01-04', price: 183.00, volume: 1300000 },
      { date: '2024-01-05', price: 185.50, volume: 1600000 }
    ]
  }
};

export class ApiClient {
  async fetchStockData(symbol: string) {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const mockData = MOCK_STOCK_DATA[symbol] || {
      price: 100 + Math.random() * 100,
      change: -5 + Math.random() * 10,
      changePercent: -5 + Math.random() * 10,
      volume: Math.floor(Math.random() * 10000000),
      previousClose: 100 + Math.random() * 100,
      historicalData: []
    };

    return mockData;
  }

  async searchSymbols(query: string): Promise<string[]> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 300));
    
    // Filter mock symbols based on query
    return MOCK_SYMBOLS.filter(symbol => 
      symbol.toLowerCase().includes(query.toLowerCase())
    );
  }
}