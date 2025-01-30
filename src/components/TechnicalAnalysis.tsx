import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer,
  AreaChart, Area
} from 'recharts';

const TechnicalAnalysis = ({ data }) => {
  // Calculate moving averages
  const calculateMA = (data, period) => {
    return data.map((item, index) => {
      if (index < period - 1) return { ...item, ma: null };
      const slice = data.slice(index - period + 1, index + 1);
      const average = slice.reduce((sum, item) => sum + item.price, 0) / period;
      return { ...item, [`ma${period}`]: average };
    });
  };

  const dataWithMA = calculateMA(calculateMA(data, 20), 50);

  return (
    <div className="space-y-6">
      {/* Price with Moving Averages */}
      <Card>
        <CardHeader>
          <CardTitle>Price and Moving Averages</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-96">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={dataWithMA}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="price" 
                  stroke="#2563eb" 
                  dot={false}
                />
                <Line 
                  type="monotone" 
                  dataKey="ma20" 
                  stroke="#dc2626" 
                  dot={false}
                />
                <Line 
                  type="monotone" 
                  dataKey="ma50" 
                  stroke="#16a34a" 
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* RSI Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Relative Strength Index (RSI)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="rsi" 
                  stroke="#8b5cf6" 
                  dot={false}
                />
                {/* Overbought/Oversold lines */}
                <Line 
                  type="monotone" 
                  dataKey="overbought" 
                  stroke="#dc2626" 
                  strokeDasharray="3 3"
                />
                <Line 
                  type="monotone" 
                  dataKey="oversold" 
                  stroke="#16a34a" 
                  strokeDasharray="3 3"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* MACD Chart */}
      <Card>
        <CardHeader>
          <CardTitle>MACD</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Area 
                  type="monotone" 
                  dataKey="macd" 
                  fill="#93c5fd" 
                  stroke="#2563eb"
                />
                <Line 
                  type="monotone" 
                  dataKey="signal" 
                  stroke="#dc2626" 
                  dot={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Bollinger Bands */}
      <Card>
        <CardHeader>
          <CardTitle>Bollinger Bands</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="price" 
                  stroke="#2563eb" 
                  dot={false}
                />
                <Line 
                  type="monotone" 
                  dataKey="upperBand" 
                  stroke="#dc2626" 
                  dot={false}
                  strokeDasharray="3 3"
                />
                <Line 
                  type="monotone" 
                  dataKey="lowerBand" 
                  stroke="#16a34a" 
                  dot={false}
                  strokeDasharray="3 3"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default TechnicalAnalysis;