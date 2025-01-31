"use client";

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer,
  Bar, BarChart
} from 'recharts';

interface SentimentAnalysis {
  news_sentiment: {
    average_score: number;
    article_count: number;
    daily_scores: Array<{
      date: string;
      avg_sentiment: number;
      article_count: number;
    }>;
  };
  social_sentiment: {
    average_score: number;
    post_count: number;
    total_engagement: number;
    daily_scores: Array<{
      date: string;
      avg_sentiment: number;
      post_count: number;
      total_engagement: number;
    }>;
  };
  overall_sentiment: {
    score: number;
    trend: string;
  };
}

const SentimentGauge = ({ score }: { score: number }) => {
  // Convert score from [-1, 1] to [0, 100]
  const percentage = ((score + 1) / 2) * 100;
  
  // Determine color based on score
  let color = '#10B981'; // Green for positive
  if (score < -0.2) color = '#EF4444'; // Red for negative
  else if (score < 0.2) color = '#F59E0B'; // Yellow for neutral
  
  return (
    <div className="relative w-48 h-48 mx-auto">
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="text-3xl font-bold">{percentage.toFixed(1)}%</div>
      </div>
      <svg className="w-full h-full transform -rotate-90">
        <circle
          cx="96"
          cy="96"
          r="88"
          fill="none"
          stroke="#E5E7EB"
          strokeWidth="12"
        />
        <circle
          cx="96"
          cy="96"
          r="88"
          fill="none"
          stroke={color}
          strokeWidth="12"
          strokeDasharray={`${(percentage * 5.53).toFixed(0)} 553`}
        />
      </svg>
    </div>
  );
};

export default function SentimentAnalysis({ data }: { data?: SentimentAnalysis }) {
  if (!data) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Sentiment Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-80">
            <p className="text-muted-foreground">No sentiment data available</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="grid gap-4">
      {/* Overall Sentiment */}
      <Card>
        <CardHeader>
          <CardTitle>Overall Sentiment</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center gap-4">
            <SentimentGauge score={data.overall_sentiment.score} />
            <div className="text-lg font-medium capitalize">
              Trend: {data.overall_sentiment.trend}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* News Sentiment Trend */}
      <Card>
        <CardHeader>
          <CardTitle>News Sentiment Trend</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data.news_sentiment.daily_scores}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="avg_sentiment"
                  stroke="#8884d8"
                  name="Sentiment Score"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Social Sentiment Analytics */}
      <Card>
        <CardHeader>
          <CardTitle>Social Media Engagement</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.social_sentiment.daily_scores}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar
                  dataKey="total_engagement"
                  fill="#82ca9d"
                  name="Engagement"
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>News Coverage</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {data.news_sentiment.article_count} articles
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Social Media Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {data.social_sentiment.post_count} posts
            </div>
            <div className="text-sm text-muted-foreground">
              {data.social_sentiment.total_engagement.toLocaleString()} engagements
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}