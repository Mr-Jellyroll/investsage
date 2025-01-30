"use client";

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer,
  AreaChart, Area, BarChart, Bar
} from 'recharts';

interface TechnicalAnalysisProps {
  data: Array<{
    date: string;
    price: number;
    volume: number;
  }>;
}

const TechnicalAnalysis = ({ data }: TechnicalAnalysisProps) => {
  // Calculate simple moving averages
  const calculateSMA = (period: number) => {
    return data.map((item, index) => {
      if (index < period - 1) return { ...item, [`sma${period}`]: null };
      const sum = data.slice(index - period + 1, index + 1)
        .reduce((acc, cur) => acc + cur.price, 0);
      return { ...item, [`sma${period}`]: sum / period };
    });
  };

  const dataWithSMA = calculateSMA(20);

  return (
    <div className="space-y-6">
      {/* Price Chart with SMA */}
      <Card>
        <CardHeader>
          <CardTitle>Price Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-96">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={dataWithSMA}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date"
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => new Date(value).toLocaleDateString()}
                />
                <YAxis 
                  domain={['auto', 'auto']}
                  tick={{ fontSize: 12 }}
                />
                <Tooltip
                  labelFormatter={(label) => new Date(label).toLocaleDateString()}
                  formatter={(value: number) => ['$' + value.toFixed(2)]}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="price" 
                  stroke="#2563eb" 
                  name="Price"
                  dot={false}
                />
                <Line 
                  type="monotone" 
                  dataKey="sma20" 
                  stroke="#dc2626" 
                  name="20-day SMA"
                  dot={false}
                  strokeDasharray="5 5"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Volume Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Volume Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date"
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => new Date(value).toLocaleDateString()}
                />
                <YAxis 
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => (value / 1000000).toFixed(1) + 'M'}
                />
                <Tooltip
                  labelFormatter={(label) => new Date(label).toLocaleDateString()}
                  formatter={(value: number) => [
                    (value / 1000000).toFixed(2) + 'M',
                    'Volume'
                  ]}
                />
                <Bar 
                  dataKey="volume" 
                  fill="#3b82f6" 
                  name="Volume"
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Price Range Analysis */}
      <Card>
        <CardHeader>
          <CardTitle>Price Trend</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date"
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => new Date(value).toLocaleDateString()}
                />
                <YAxis 
                  domain={['auto', 'auto']}
                  tick={{ fontSize: 12 }}
                />
                <Tooltip
                  labelFormatter={(label) => new Date(label).toLocaleDateString()}
                  formatter={(value: number) => ['$' + value.toFixed(2), 'Price']}
                />
                <Area 
                  type="monotone" 
                  dataKey="price"
                  stroke="#2563eb"
                  fill="#93c5fd"
                  name="Price"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default TechnicalAnalysis;