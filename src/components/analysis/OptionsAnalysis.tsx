"use client";

import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer,
  ScatterChart, Scatter,
  BarChart, Bar
} from 'recharts';

interface Greeks {
  delta: number;
  gamma: number;
  theta: number;
  vega: number;
  rho: number;
}

interface Option {
  strike: number;
  expiry_days: number;
  bid: number;
  ask: number;
  volume: number;
  open_interest: number;
  implied_volatility: number;
  greeks: Greeks;
}

interface OptionsAnalysis {
  summary: {
    current_price: number;
    implied_volatility: number;
    put_call_ratio: number;
    most_active_strikes: Option[];
  };
  calls: Option[];
  puts: Option[];
  greeks: Greeks;
  volume_distribution: {
    by_expiry: Record<string, number>;
    by_strike: Record<string, number>;
  };
}

export default function OptionsAnalysis({ data }: { data?: OptionsAnalysis }) {
  const [selectedExpiry, setSelectedExpiry] = useState<number>();

  if (!data) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Options Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-80">
            <p className="text-muted-foreground">No options data available</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Filter options by selected expiry
  const filteredCalls = selectedExpiry
    ? data.calls.filter(opt => opt.expiry_days === selectedExpiry)
    : data.calls;

  const filteredPuts = selectedExpiry
    ? data.puts.filter(opt => opt.expiry_days === selectedExpiry)
    : data.puts;

  // Prepare volume distribution data
  const volumeData = Object.entries(data.volume_distribution.by_strike)
    .map(([strike, volume]) => ({
      strike: parseFloat(strike),
      volume
    }))
    .sort((a, b) => a.strike - b.strike);

  // Prepare Greeks data for chart
  const greeksData = [
    { name: 'Delta', value: data.greeks.delta },
    { name: 'Gamma', value: data.greeks.gamma * 100 }, // Scale gamma for visibility
    { name: 'Theta', value: data.greeks.theta / 100 }, // Scale theta for visibility
    { name: 'Vega', value: data.greeks.vega / 10 },    // Scale vega for visibility
    { name: 'Rho', value: data.greeks.rho }
  ];

  return (
    <div className="grid gap-4">
      {/* Summary Cards */}
      <div className="grid grid-cols-4 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Current Price</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${data.summary.current_price.toFixed(2)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Implied Volatility</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {(data.summary.implied_volatility * 100).toFixed(1)}%
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Put/Call Ratio</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {data.summary.put_call_ratio.toFixed(2)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Total Volume</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {Object.values(data.volume_distribution.by_strike).reduce((a, b) => a + b, 0).toLocaleString()}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Options Chain Visualization */}
      <Card>
        <CardHeader>
          <CardTitle>Options Chain</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="strike" 
                  type="number" 
                  domain={['auto', 'auto']} 
                  name="Strike" 
                />
                <YAxis 
                  dataKey="volume" 
                  name="Volume" 
                />
                <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                <Legend />
                <Scatter 
                  name="Calls" 
                  data={filteredCalls} 
                  fill="#82ca9d" 
                />
                <Scatter 
                  name="Puts" 
                  data={filteredPuts} 
                  fill="#8884d8" 
                />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Greeks Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Option Greeks</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={greeksData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Volume Distribution */}
      <Card>
        <CardHeader>
          <CardTitle>Volume Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={volumeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="strike" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="volume" fill="#10b981" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Most Active Options */}
      <Card>
        <CardHeader>
          <CardTitle>Most Active Options</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-2">
            {data.summary.most_active_strikes.map((option, index) => (
              <div key={index} className="flex justify-between items-center p-2 bg-muted rounded">
                <span>Strike ${option.strike}</span>
                <span>{option.expiry_days}d</span>
                <span>Vol: {option.volume.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}