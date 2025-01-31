"use client";

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar
} from 'recharts';

interface MLAnalysis {
  predictions: Array<{
    date: string;
    price: number;
  }>;
  confidence_scores: number[];
  feature_importance: {
    [key: string]: number;
  };
}

export default function MLAnalysis({ data }: { data?: MLAnalysis }) {
  if (!data?.predictions.length) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>ML Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-80">
            <p className="text-muted-foreground">No prediction data available</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Prepare data for feature importance chart
  const featureData = Object.entries(data.feature_importance).map(([feature, importance]) => ({
    feature: feature.toUpperCase(),
    importance: parseFloat((importance * 100).toFixed(1))
  }));

  // Prepare data for confidence chart
  const confidenceData = data.predictions.map((pred, index) => ({
    date: pred.date,
    confidence: parseFloat((data.confidence_scores[index] * 100).toFixed(1))
  }));

  return (
    <div className="grid gap-4">
      {/* Price Predictions */}
      <Card>
        <CardHeader>
          <CardTitle>Price Predictions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data.predictions}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip 
                  formatter={(value: any) => [`$${value}`, 'Price']}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="price" 
                  stroke="#2563eb"
                  name="Predicted Price"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Confidence Scores */}
      <Card>
        <CardHeader>
          <CardTitle>Prediction Confidence</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={confidenceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis domain={[0, 100]} />
                <Tooltip 
                  formatter={(value: any) => [`${value}%`, 'Confidence']}
                />
                <Line
                  type="monotone"
                  dataKey="confidence"
                  stroke="#10b981"
                  name="Confidence"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Feature Importance */}
      <Card>
        <CardHeader>
          <CardTitle>Feature Importance</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={featureData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="feature" />
                <YAxis domain={[0, 100]} />
                <Tooltip 
                  formatter={(value: any) => [`${value}%`, 'Importance']}
                />
                <Bar 
                  dataKey="importance" 
                  fill="#3b82f6"
                  name="Feature Importance"
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}