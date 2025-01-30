import React, { useState, useEffect } from 'react';
import StockSearch from './StockSearch';
import StockOverview from './StockOverview';
import TechnicalAnalysis from './TechnicalAnalysis';
import { ApiClient } from '@/lib/api-client';

const Dashboard = () => {
  const [selectedStock, setSelectedStock] = useState<string>('');
  const [stockData, setStockData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const apiClient = new ApiClient();

  useEffect(() => {
    const fetchStockData = async () => {
      if (!selectedStock) return;

      setIsLoading(true);
      try {
        const data = await apiClient.fetchStockData(selectedStock);
        setStockData(data);
      } catch (error) {
        console.error('Error fetching stock data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchStockData();
  }, [selectedStock]);

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col space-y-4">
        <h1 className="text-3xl font-bold">Investment Dashboard</h1>
        <StockSearch onSelectStock={setSelectedStock} />
      </div>

      {isLoading && (
        <div className="text-center py-8">
          <p className="text-muted-foreground">Loading...</p>
        </div>
      )}

      {stockData && (
        <>
          <StockOverview 
            symbol={selectedStock}
            data={{
              price: stockData.price,
              change: stockData.change,
              changePercent: stockData.changePercent,
              volume: stockData.volume,
              previousClose: stockData.previousClose,
            }}
          />

          <TechnicalAnalysis data={stockData.historicalData} />
        </>
      )}

      {!selectedStock && !isLoading && (
        <div className="text-center py-12">
          <h2 className="text-2xl font-semibold text-muted-foreground">
            Search for a stock to begin
          </h2>
          <p className="text-muted-foreground mt-2">
            Enter a stock symbol to view detailed analysis
          </p>
        </div>
      )}
    </div>
  );
};

export default Dashboard;