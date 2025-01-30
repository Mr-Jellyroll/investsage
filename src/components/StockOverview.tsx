"use client";

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { ArrowUp, ArrowDown, LineChart, BarChart2, TrendingUp } from "lucide-react";

interface StockOverviewProps {
  symbol: string;
  data: {
    price: number;
    change: number;
    changePercent: number;
    volume: number;
    previousClose: number;
  };
}

const StockOverview = ({ symbol, data }: StockOverviewProps) => {
  const isPositive = data.change >= 0;

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Current Price</CardTitle>
          <LineChart className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">${data.price.toFixed(2)}</div>
          <div className={`flex items-center text-sm ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
            {isPositive ? <ArrowUp className="h-4 w-4 mr-1" /> : <ArrowDown className="h-4 w-4 mr-1" />}
            {Math.abs(data.changePercent).toFixed(2)}%
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Volume</CardTitle>
          <BarChart2 className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {(data.volume / 1000000).toFixed(2)}M
          </div>
          <p className="text-xs text-muted-foreground">Daily Volume</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Change</CardTitle>
          <TrendingUp className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className={`text-2xl font-bold ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
            ${Math.abs(data.change).toFixed(2)}
          </div>
          <p className="text-xs text-muted-foreground">From Previous Close</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Previous Close</CardTitle>
          <LineChart className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">${data.previousClose.toFixed(2)}</div>
          <p className="text-xs text-muted-foreground">Last Trading Day</p>
        </CardContent>
      </Card>
    </div>
  );
};

export default StockOverview;