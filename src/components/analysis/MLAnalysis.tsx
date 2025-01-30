"use client";

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer, BarChart, Bar
} from 'recharts';

interface MLAnalysisProps {
  data: {
    predictions: number[];
    confidence: number;
    important_features: Record<string, number>;
  };
}

const MLAnalysis = ({ data }: MLAnalysisProps) => {
  const predictionData = data.predictions.map((value, index) => ({
    day: `Day ${index + 1}`,
    price: value
  }));

  const featureData = Object.entries(data.important_features).map(([feature, importance]) => ({
    feature,
    importance
  }));

  return (
    <div className="grid gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Price Predictions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={predictionData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis />
                <Tooltip />
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
                <YAxis />
                <Tooltip />
                <Bar dataKey="importance" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Model Confidence</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center">
            <div className="text-5xl font-bold text-blue-600">
              {(data.confidence * 100).toFixed(1)}%
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default MLAnalysis;