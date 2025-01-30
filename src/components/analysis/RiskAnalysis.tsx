"use client";

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import {
  RadarChart, PolarGrid, PolarAngleAxis, 
  PolarRadiusAxis, Radar, ResponsiveContainer,
  LineChart, Line, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend
} from 'recharts';

interface RiskAnalysisProps {
  data: {
    volatility: number;
    var_95: number;
    var_99: number;
    sharpe_ratio: number;
    sortino_ratio: number;
    max_drawdown: number;
    beta: number;
    correlation_matrix: Record<string, number>;
  };
}

const RiskAnalysis = ({ data }: RiskAnalysisProps) => {
  const riskMetrics = [
    { metric: 'Volatility', value: data.volatility },
    { metric: 'VaR (95%)', value: data.var_95 },
    { metric: 'Max Drawdown', value: data.max_drawdown },
    { metric: 'Beta', value: data.beta },
    { metric: 'Sharpe Ratio', value: data.sharpe_ratio }
  ];

  return (
    <div className="grid gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Risk Metrics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={riskMetrics}>
                <PolarGrid />
                <PolarAngleAxis dataKey="metric" />
                <PolarRadiusAxis />
                <Radar
                  name="Risk Profile"
                  dataKey="value"
                  stroke="#2563eb"
                  fill="#93c5fd"
                  fillOpacity={0.6}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Value at Risk (95%)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {(data.var_95 * 100).toFixed(2)}%
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Sharpe Ratio</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {data.sharpe_ratio.toFixed(2)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Beta</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {data.beta.toFixed(2)}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default RiskAnalysis;