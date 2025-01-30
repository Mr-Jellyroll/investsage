"use client";

import React, { useState, useEffect } from 'react';
import StockSearch from '@/components/StockSearch';
import StockOverview from '@/components/StockOverview';
import TabsAnalysis from '@/components/TabsAnalysis';
import { ApiClient } from '@/lib/api-client';
import { Card, CardContent } from "@/components/ui/card";

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
      {/* Header and Search */}
      <div className="flex flex-col space-y-4">
        <h1 className="text-3xl font-bold">Investment Dashboard</h1>
        <StockSearch onSelectStock={setSelectedStock} />
      </div>

      {isLoading && (
        <Card>
          <CardContent className="flex items-center justify-center py-8">
            <div className="text-center text-muted-foreground">Loading...</div>
          </CardContent>
        </Card>
      )}

      {stockData && (
        <div className="space-y-6">
          {/* Overview Cards */}
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

          {/* Analysis Tabs */}
          <TabsAnalysis 
            symbol={selectedStock}
            data={{
              technical: stockData.technical,
              ml: stockData.ml,
              options: stockData.options,
              portfolio: stockData.portfolio,
              risk: stockData.risk,
              sentiment: stockData.sentiment
            }}
          />
        </div>
      )}

      {!selectedStock && !isLoading && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <h2 className="text-2xl font-semibold text-muted-foreground">
              Search for a stock to begin
            </h2>
            <p className="text-muted-foreground mt-2">
              Enter a stock symbol to view detailed analysis
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default Dashboard;