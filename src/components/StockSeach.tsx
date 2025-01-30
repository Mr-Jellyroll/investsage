"use client";

import React, { useState, useEffect } from 'react';
import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { ApiClient } from '@/lib/api-client';

interface StockSearchProps {
  onSelectStock: (symbol: string) => void;
}

const StockSearch = ({ onSelectStock }: StockSearchProps) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const apiClient = new ApiClient();

  useEffect(() => {
    const searchStocks = async () => {
      if (query.length < 1) {
        setResults([]);
        return;
      }

      setIsLoading(true);
      try {
        const symbols = await apiClient.searchSymbols(query);
        setResults(symbols);
      } catch (error) {
        console.error('Error searching symbols:', error);
        setResults([]);
      } finally {
        setIsLoading(false);
      }
    };

    const timeoutId = setTimeout(searchStocks, 300);
    return () => clearTimeout(timeoutId);
  }, [query]);

  return (
    <div className="relative w-full max-w-md">
      <div className="relative">
        <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search stocks..."
          value={query}
          onChange={(e) => setQuery(e.target.value.toUpperCase())}
          className="pl-8"
        />
      </div>
      
      {(results.length > 0 || isLoading) && (
        <Card className="absolute mt-1 w-full z-10 max-h-60 overflow-auto">
          {isLoading ? (
            <div className="p-4 text-center text-muted-foreground">Loading...</div>
          ) : (
            <ul className="py-2">
              {results.map((symbol) => (
                <li
                  key={symbol}
                  className="px-4 py-2 hover:bg-muted cursor-pointer"
                  onClick={() => {
                    onSelectStock(symbol);
                    setQuery('');
                    setResults([]);
                  }}
                >
                  {symbol}
                </li>
              ))}
            </ul>
          )}
        </Card>
      )}
    </div>
  );
};

export default StockSearch;