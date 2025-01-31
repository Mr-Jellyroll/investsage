"use client";

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer
} from 'recharts';

interface TechnicalAnalysis {
  trend_indicators?: {
    moving_averages: Array<{
      date: string;
      close: number;
      sma_20: number;
      sma_50: number;
      ema_12: number;
      ema_26: number;
    }>;
    trend: string;
  };
  momentum_indicators?: {
    rsi: number;
  };
  volume_indicators?: {
    average_volume: number;
    volume_trend: string;
  };
}

export default function TechnicalAnalysis({ data }: { data?: TechnicalAnalysis }) {
  if (!data?.trend_indicators?.moving_averages?.length) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Technical Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-80">
            <p className="text-muted-foreground">No technical data available</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="grid gap-4">
      {/* Moving Averages Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Moving Averages</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data.trend_indicators.moving_averages}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="close" 
                  stroke="#333" 
                  dot={false}
                  name="Price" 
                />
                <Line 
                  type="monotone" 
                  dataKey="sma_20" 
                  stroke="#8884d8" 
                  dot={false}
                  name="SMA 20" 
                />
                <Line 
                  type="monotone" 
                  dataKey="sma_50" 
                  stroke="#82ca9d" 
                  dot={false}
                  name="SMA 50" 
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Indicators Summary */}
      <div className="grid grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Trend</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold capitalize">
              {data.trend_indicators.trend}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>RSI</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {data.momentum_indicators?.rsi.toFixed(2)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Volume Trend</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold capitalize">
              {data.volume_indicators?.volume_trend}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}