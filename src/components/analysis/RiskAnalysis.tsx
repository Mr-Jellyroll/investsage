"use client";

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer,
  RadarChart, PolarGrid, PolarAngleAxis, 
  PolarRadiusAxis, Radar,
  BarChart, Bar
} from 'recharts';

interface RiskAnalysis {
  volatility_metrics: {
    daily_volatility: number;
    annual_volatility: number;
    current_volatility: number;
    beta: number;
    r_squared: number;
  };
  value_at_risk: {
    historical_var_95: number;
    historical_var_99: number;
    conditional_var_95: number;
    conditional_var_99: number;
    parametric_var_95: number;
    parametric_var_99: number;
  };
  ratios: {
    sharpe_ratio: number;
    sortino_ratio: number;
    treynor_ratio: number;
    information_ratio: number;
  };
  correlations: {
    market: number;
    market_up: number;
    market_down: number;
  };
  drawdown_analysis: {
    max_drawdown: number;
    avg_drawdown: number;
    drawdown_duration: number;
    recovery_time: number;
  };
  stress_test: {
    market_crash: number;
    high_volatility: number;
    correlation_breakdown: number;
    liquidity_crisis: number;
  };
}

export default function RiskAnalysis({ data }: { data?: RiskAnalysis }) {
  if (!data) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Risk Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-80">
            <p className="text-muted-foreground">No risk data available</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Prepare data for ratio radar chart
  const ratioData = [
    {
      metric: "Sharpe",
      value: data.ratios.sharpe_ratio
    },
    {
      metric: "Sortino",
      value: data.ratios.sortino_ratio
    },
    {
      metric: "Treynor",
      value: data.ratios.treynor_ratio
    },
    {
      metric: "Information",
      value: data.ratios.information_ratio
    }
  ];

  // Prepare stress test data
  const stressTestData = Object.entries(data.stress_test).map(([scenario, value]) => ({
    scenario: scenario.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' '),
    impact: Math.abs(value) * 100
  }));

  // Prepare VaR data
  const varData = [
    { name: '95% VaR', historical: data.value_at_risk.historical_var_95 * 100, conditional: data.value_at_risk.conditional_var_95 * 100 },
    { name: '99% VaR', historical: data.value_at_risk.historical_var_99 * 100, conditional: data.value_at_risk.conditional_var_99 * 100 }
  ];

  return (
    <div className="grid gap-4">
      {/* Key Risk Metrics */}
      <div className="grid grid-cols-4 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Beta</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {data.volatility_metrics.beta.toFixed(2)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Annual Volatility</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {(data.volatility_metrics.annual_volatility * 100).toFixed(1)}%
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Max Drawdown</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-500">
              {(data.drawdown_analysis.max_drawdown * 100).toFixed(1)}%
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recovery Time</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {data.drawdown_analysis.recovery_time} days
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Risk Ratios Radar */}
      <Card>
        <CardHeader>
          <CardTitle>Risk-Adjusted Return Ratios</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={ratioData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="metric" />
                <PolarRadiusAxis />
                <Radar
                  name="Risk Ratios"
                  dataKey="value"
                  stroke="#2563eb"
                  fill="#3b82f6"
                  fillOpacity={0.6}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Value at Risk */}
      <Card>
        <CardHeader>
          <CardTitle>Value at Risk (VaR)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={varData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip formatter={(value) => `${value.toFixed(2)}%`} />
                <Legend />
                <Bar dataKey="historical" name="Historical VaR" fill="#3b82f6" />
                <Bar dataKey="conditional" name="Conditional VaR" fill="#ef4444" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Stress Test Results */}
      <Card>
        <CardHeader>
          <CardTitle>Stress Test Impact</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stressTestData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="scenario" />
                <YAxis />
                <Tooltip formatter={(value) => `${value.toFixed(2)}%`} />
                <Bar dataKey="impact" fill="#f59e0b" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Correlation Analysis */}
      <Card>
        <CardHeader>
          <CardTitle>Market Correlations</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-sm font-medium text-muted-foreground">Overall</div>
              <div className="text-2xl font-bold mt-1">
                {(data.correlations.market * 100).toFixed(1)}%
              </div>
            </div>
            <div className="text-center">
              <div className="text-sm font-medium text-muted-foreground">Up Market</div>
              <div className="text-2xl font-bold text-green-500 mt-1">
                {(data.correlations.market_up * 100).toFixed(1)}%
              </div>
            </div>
            <div className="text-center">
              <div className="text-sm font-medium text-muted-foreground">Down Market</div>
              <div className="text-2xl font-bold text-red-500 mt-1">
                {(data.correlations.market_down * 100).toFixed(1)}%
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}