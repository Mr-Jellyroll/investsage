"use client";

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import {
  PieChart, Pie, Cell,
  LineChart, Line, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar,
  RadarChart, PolarGrid, PolarAngleAxis, 
  PolarRadiusAxis, Radar
} from 'recharts';

interface Position {
  weight: number;
  value: number;
  price: number;
}

interface PortfolioAnalysis {
  current_allocation: {
    positions: Record<string, Position>;
    total_value: number;
    position_count: number;
  };
  risk_metrics: {
    annual_return: number;
    annual_volatility: number;
    sharpe_ratio: number;
    max_drawdown: number;
    var_95: number;
  };
  optimization: {
    optimal_weights: Record<string, number>;
    optimal_sharpe: number;
    optimization_success: boolean;
  };
  diversification: {
    avg_correlation: number;
    herfindahl_index: number;
    effective_positions: number;
    correlation_matrix: Record<string, Record<string, number>>;
  };
  rebalancing: {
    suggested_trades: Record<string, {
      current_weight: number;
      target_weight: number;
      difference: number;
    }>;
    trade_count: number;
    total_turnover: number;
  };
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

export default function PortfolioAnalysis({ data }: { data?: PortfolioAnalysis }) {
  if (!data) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Portfolio Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-80">
            <p className="text-muted-foreground">No portfolio data available</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Prepare allocation data for pie chart
  const allocationData = Object.entries(data.current_allocation.positions).map(
    ([symbol, position], index) => ({
      name: symbol,
      value: position.weight * 100,
      color: COLORS[index % COLORS.length]
    })
  );

  // Prepare optimization comparison data
  const optimizationData = Object.keys(data.optimization.optimal_weights).map(symbol => ({
    name: symbol,
    current: data.current_allocation.positions[symbol]?.weight * 100 || 0,
    optimal: data.optimization.optimal_weights[symbol] * 100
  }));

  // Prepare risk metrics for radar chart
  const riskData = [
    { metric: 'Return', value: data.risk_metrics.annual_return * 100 },
    { metric: 'Sharpe', value: data.risk_metrics.sharpe_ratio * 100 },
    { metric: 'Diversification', value: data.diversification.effective_positions * 25 }, // Scale for visibility
    { metric: 'Volatility', value: (1 - data.risk_metrics.annual_volatility) * 100 }, // Invert for radar
    { metric: 'VaR', value: (1 + data.risk_metrics.var_95) * 100 } // Invert for radar
  ];

  // Prepare rebalancing data
  const rebalancingData = Object.entries(data.rebalancing.suggested_trades)
    .map(([symbol, trade]) => ({
      symbol,
      current: trade.current_weight * 100,
      target: trade.target_weight * 100,
      difference: trade.difference * 100
    }))
    .sort((a, b) => Math.abs(b.difference) - Math.abs(a.difference));

  return (
    <div className="grid gap-4">
      {/* Portfolio Overview */}
      <div className="grid grid-cols-4 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Total Value</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${data.current_allocation.total_value.toLocaleString()}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Return</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-500">
              {(data.risk_metrics.annual_return * 100).toFixed(1)}%
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Sharpe Ratio</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {data.risk_metrics.sharpe_ratio.toFixed(2)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Positions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {data.current_allocation.position_count}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Current Allocation */}
      <Card>
        <CardHeader>
          <CardTitle>Current Allocation</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={allocationData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={120}
                  label
                >
                  {allocationData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `${value.toFixed(1)}%`} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Portfolio Risk Profile */}
      <Card>
        <CardHeader>
          <CardTitle>Risk Profile</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={riskData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="metric" />
                <PolarRadiusAxis />
                <Radar
                  name="Portfolio"
                  dataKey="value"
                  stroke="#3b82f6"
                  fill="#3b82f6"
                  fillOpacity={0.6}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Optimization Comparison */}
      <Card>
        <CardHeader>
          <CardTitle>Optimization Comparison</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={optimizationData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip formatter={(value) => `${value.toFixed(1)}%`} />
                <Legend />
                <Bar dataKey="current" name="Current Weight" fill="#3b82f6" />
                <Bar dataKey="optimal" name="Optimal Weight" fill="#10b981" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Rebalancing Suggestions */}
      <Card>
        <CardHeader>
          <CardTitle>Suggested Rebalancing</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {rebalancingData.map((trade) => (
              <div
                key={trade.symbol}
                className="grid grid-cols-4 gap-4 p-4 bg-muted rounded-lg"
              >
                <div className="font-medium">{trade.symbol}</div>
                <div className="text-right">{trade.current.toFixed(1)}%</div>
                <div className="text-right">{trade.target.toFixed(1)}%</div>
                <div className={`text-right font-bold ${trade.difference > 0 ? 'text-green-500' : 'text-red-500'}`}>
                  {trade.difference > 0 ? '+' : ''}{trade.difference.toFixed(1)}%
                </div>
              </div>
            ))}
            <div className="text-sm text-muted-foreground mt-4">
              Total Turnover: {(data.rebalancing.total_turnover * 100).toFixed(1)}%
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}