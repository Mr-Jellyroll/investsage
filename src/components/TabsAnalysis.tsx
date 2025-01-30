"use client";

import React from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card } from "@/components/ui/card";
import TechnicalAnalysis from './analysis/TechnicalAnalysis';
import MLAnalysis from './analysis/MLAnalysis';
import OptionsAnalysis from './analysis/OptionsAnalysis';
import PortfolioAnalysis from './analysis/PortfolioAnalysis';
import RiskAnalysis from './analysis/RiskAnalysis';
import SentimentAnalysis from './analysis/SentimentAnalysis';

interface TabsAnalysisProps {
  symbol: string;
  data: any; // We'll type this properly later
}

const TabsAnalysis = ({ symbol, data }: TabsAnalysisProps) => {
  return (
    <Tabs defaultValue="technical" className="w-full">
      <TabsList className="grid grid-cols-6 w-full">
        <TabsTrigger value="technical">Technical</TabsTrigger>
        <TabsTrigger value="ml">ML Predictions</TabsTrigger>
        <TabsTrigger value="options">Options</TabsTrigger>
        <TabsTrigger value="portfolio">Portfolio</TabsTrigger>
        <TabsTrigger value="risk">Risk</TabsTrigger>
        <TabsTrigger value="sentiment">Sentiment</TabsTrigger>
      </TabsList>

      <div className="mt-4">
        <TabsContent value="technical">
          <TechnicalAnalysis data={data.technical} />
        </TabsContent>

        <TabsContent value="ml">
          <MLAnalysis data={data.ml} />
        </TabsContent>

        <TabsContent value="options">
          <OptionsAnalysis data={data.options} />
        </TabsContent>

        <TabsContent value="portfolio">
          <PortfolioAnalysis data={data.portfolio} />
        </TabsContent>

        <TabsContent value="risk">
          <RiskAnalysis data={data.risk} />
        </TabsContent>

        <TabsContent value="sentiment">
          <SentimentAnalysis data={data.sentiment} />
        </TabsContent>
      </div>
    </Tabs>
  );
};

export default TabsAnalysis;