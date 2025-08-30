// Investment Opportunities Service for handling all API communication
import config from './config';

export interface InvestmentOpportunity {
  id: string;
  address: string;
  price: number;
  estimated_value: number;
  equity_gain: number;
  equity_percentage: number;
  property_type: string;
  beds: number;
  baths: number;
  sqft: number;
  janus_score: number;
  distress_level: string;
  cap_rate: number;
  roi_estimate: number;
  strategy: string;
  risk_level: string;
  market_trend: string;
  last_updated: string;
  analysis_timestamp: string;
  agent_insights: string[];
  data_sources: string[];
  image_url?: string;
}

export interface InvestmentOpportunityResponse {
  opportunities: InvestmentOpportunity[];
  summary: {
    total_opportunities: number;
    filtered_count: number;
    average_price: number;
    average_equity_gain: number;
    average_cap_rate: number;
    average_janus_score: number;
    strategies_available: string[];
    risk_levels_available: string[];
    property_types_available: string[];
  };
  filters_applied: Record<string, any>;
  last_updated: string;
}

export interface MarketAnalysis {
  market_trend: string;
  average_cap_rate: number;
  price_appreciation: number;
  rental_demand: string;
  neighborhood_score: number;
  risk_factors: string[];
  opportunities: string[];
}

export interface InvestmentFilters {
  limit?: number;
  min_price?: number;
  max_price?: number;
  property_type?: string;
  min_beds?: number;
  max_beds?: number;
  min_janus_score?: number;
  strategy?: string;
  risk_level?: string;
  neighborhood?: string;
}

class InvestmentOpportunitiesService {
  private baseUrl: string;
  private timeout: number;

  constructor() {
    this.baseUrl = config.api.baseUrl;
    this.timeout = config.api.timeout;
  }

  private async makeRequest<T>(
    endpoint: string, 
    options?: RequestInit,
    customTimeout?: number
  ): Promise<T> {
    const controller = new AbortController();
    const timeoutId = setTimeout(
      () => controller.abort(), 
      customTimeout || this.timeout
    );

    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
        },
        signal: controller.signal,
        ...options,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      return await response.json();
    } catch (error) {
      clearTimeout(timeoutId);
      
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          throw new Error('Request timeout');
        }
        throw error;
      }
      
      console.error('Investment opportunities service error:', error);
      throw new Error('Network error');
    }
  }

  // Get investment opportunities with optional filtering
  async getInvestmentOpportunities(filters?: InvestmentFilters): Promise<InvestmentOpportunityResponse> {
    const params = new URLSearchParams();
    
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, value.toString());
        }
      });
    }

    const endpoint = `/api/v1/investment-opportunities/opportunities${params.toString() ? `?${params.toString()}` : ''}`;
    return this.makeRequest<InvestmentOpportunityResponse>(endpoint);
  }

  // Get market analysis
  async getMarketAnalysis(): Promise<MarketAnalysis> {
    return this.makeRequest<MarketAnalysis>('/api/v1/investment-opportunities/market-analysis');
  }

  // Get specific investment opportunity by ID
  async getInvestmentOpportunity(opportunityId: string): Promise<InvestmentOpportunity> {
    return this.makeRequest<InvestmentOpportunity>(`/api/v1/investment-opportunities/opportunities/${opportunityId}`);
  }

  // Get investment summary
  async getInvestmentSummary(): Promise<any> {
    return this.makeRequest<any>('/api/v1/investment-opportunities/summary');
  }

  // Quick connection test
  async testConnection(): Promise<boolean> {
    try {
      await this.getInvestmentSummary();
      return true;
    } catch {
      return false;
    }
  }

  // Get service info
  getServiceInfo() {
    return {
      baseUrl: this.baseUrl,
      timeout: this.timeout,
      endpoints: {
        opportunities: '/api/v1/investment-opportunities/opportunities',
        marketAnalysis: '/api/v1/investment-opportunities/market-analysis',
        summary: '/api/v1/investment-opportunities/summary'
      }
    };
  }
}

export const investmentOpportunitiesService = new InvestmentOpportunitiesService();
export default investmentOpportunitiesService;
