
import { AnalysisType } from '@/types/api';

export interface AnalysisRequest {
  symbol: string;
  analysisType: AnalysisType;
  startDate?: string;
  endDate?: string;
  params?: Record<string, unknown>;
}

export interface AnalysisResponse {
  success: boolean;
  data?: Record<string, unknown>;
  error?: string;
  warnings?: string[];
  metadata?: Record<string, unknown>;
}

export class InvestSageAPI {
  private baseUrl: string;

  constructor(baseUrl = '/api') {
    this.baseUrl = baseUrl;
  }

  /**
   * Perform analysis on a symbol
   */
  async analyze(request: AnalysisRequest): Promise<AnalysisResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      };
    }
  }

  /**
   * Get list of symbols
   */
  async getAvailableSymbols(): Promise<string[]> {
    try {
      const response = await fetch(`${this.baseUrl}/symbols`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching symbols:', error);
      return [];
    }
  }

  /**
   * Get available analysis
   */
  async getAnalysisCapabilities(): Promise<Record<string, unknown>> {
    try {
      const response = await fetch(`${this.baseUrl}/capabilities`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching capabilities:', error);
      return {};
    }
  }

  /**
   * Check system status
   */
  async getStatus(): Promise<{
    status: 'ok' | 'error';
    message?: string;
  }> {
    try {
      const response = await fetch(`${this.baseUrl}/status`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      return {
        status: 'error',
        message: error instanceof Error ? error.message : 'Unknown error occurred',
      };
    }
  }
}

export const investSageAPI = new InvestSageAPI();