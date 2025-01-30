"use client";

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer
} from 'recharts';

interface PortfolioAnalysisProps {
  data: {
    allocations: { sector: string; percentage: number }[];
  };
}

const COLORS = ["#2563eb", "#ef4444", "#fbbf24", "#10b981", "#8b5cf6"];

const PortfolioAnalysis = ({ data }: PortfolioAnalysisProps) => {
  return (
    <div className="grid gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Portfolio Allocation</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data.allocations}
                  dataKey="percentage"
                  nameKey="sector"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  fill="#2563eb"
                  label
                >
                  {data.allocations.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default PortfolioAnalysis;
