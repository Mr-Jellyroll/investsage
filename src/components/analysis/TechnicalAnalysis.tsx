"use client";

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

interface TechnicalAnalysisProps {
  data: {
    moving_averages: { day: number; sma: number; ema: number }[];
    rsi: number[];
  };
}

const TechnicalAnalysis = ({ data }: TechnicalAnalysisProps) => {
  return (
    <div className="grid gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Moving Averages</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data.moving_averages}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="sma" stroke="#2563eb" name="SMA" />
                <Line type="monotone" dataKey="ema" stroke="#ef4444" name="EMA" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>RSI (Relative Strength Index)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {data.rsi[data.rsi.length - 1].toFixed(2)}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default TechnicalAnalysis;
