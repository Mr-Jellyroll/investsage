"use client";

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';

interface OptionsAnalysisProps {
  data: {
    open_interest: { strike: number; calls: number; puts: number }[];
    implied_volatility: { strike: number; iv: number }[];
  };
}

const OptionsAnalysis = ({ data }: OptionsAnalysisProps) => {
  return (
    <div className="grid gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Open Interest (Calls vs. Puts)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.open_interest}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="strike" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="calls" fill="#2563eb" name="Calls" />
                <Bar dataKey="puts" fill="#ef4444" name="Puts" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Implied Volatility</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.implied_volatility}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="strike" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="iv" fill="#fbbf24" name="IV" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default OptionsAnalysis;
