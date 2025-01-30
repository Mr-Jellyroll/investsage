"use client";

import React from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import TechnicalAnalysis from "./analysis/TechnicalAnalysis";
import OptionsAnalysis from "./analysis/OptionsAnalysis";
import PortfolioAnalysis from "./analysis/PortfolioAnalysis";
import SentimentAnalysis from "./analysis/SentimentAnalysis";
import MLAnalysis from "./analysis/MLAnalysis";
import RiskAnalysis from "./analysis/RiskAnalysis";

interface TabsAnalysisProps {
  data: {
    technical: any;
    options: any;
    portfolio: any;
    sentiment: any;
    ml: any;
    risk: any;
  };
}

const TabsAnalysis = ({ data }: TabsAnalysisProps) => {
  if (!data) {
    return <div>Loading analysis data...</div>;
  }

  return (
    <Tabs defaultValue="technical" className="w-full">
      <TabsList className="flex gap-2 border-b p-2">
        <TabsTrigger value="technical">Technical</TabsTrigger>
        <TabsTrigger value="options">Options</TabsTrigger>
        <TabsTrigger value="portfolio">Portfolio</TabsTrigger>
        <TabsTrigger value="sentiment">Sentiment</TabsTrigger>
        <TabsTrigger value="ml">ML Analysis</TabsTrigger>
        <TabsTrigger value="risk">Risk</TabsTrigger>
      </TabsList>

      <TabsContent value="technical">
        <TechnicalAnalysis data={data.technical} />
      </TabsContent>
      <TabsContent value="options">
        <OptionsAnalysis data={data.options} />
      </TabsContent>
      <TabsContent value="portfolio">
        <PortfolioAnalysis data={data.portfolio} />
      </TabsContent>
      <TabsContent value="sentiment">
        <SentimentAnalysis data={data.sentiment} />
      </TabsContent>
      <TabsContent value="ml">
        <MLAnalysis data={data.ml} />
      </TabsContent>
      <TabsContent value="risk">
        <RiskAnalysis data={data.risk} />
      </TabsContent>
    </Tabs>
  );
};

export default TabsAnalysis;
