// Real Estate APIs Service for handling live property data
import config from './config';

export interface PropertyData {
  id: string;
  address: string;
  price?: number;
  estimated_value?: number;
  property_type: string;
  beds?: number;
  baths?: number;
  sqft?: number;
  lot_size?: number;
  year_built?: number;
  last_sold_date?: string;
  last_sold_price?: number;
  tax_assessment?: number;
  market_trend: string;
  data_source: string;
  last_updated: string;
  api_confidence: number;
}

export interface MarketData {
  date: string;
  median_price?: number;
  sales_volume?: number;
  days_on_market?: number;
  inventory_level?: number;
  mortgage_rate?: number;
  data_source: string;
}

export interface RealEstateAPIResponse {
  properties: PropertyData[];
  market_data: MarketData;
  summary: {
    total_properties: number;
    filtered_count: number;
    average_price: number;
    average_estimated_value: number;
    property_types_available: string[];
    market_trends: string[];
    api_confidence_avg: number;
    data_sources: string[];
  };
  last_updated: string;
}

export interface APIStatus {
  estated_api: {
    available: boolean;
    key_configured: boolean;
    status: string;
  };
  attom_api: {
    available: boolean;
    key_configured: boolean;
    status: string;
  };
  fred_api: {
    available: boolean;
    key_configured: boolean;
    status: string;
  };
  last_checked: string;
}

export interface PropertyFilters {
  limit?: number;
  address?: string;
  property_type?: string;
  min_price?: number;
  max_price?: number;
}

class RealEstateAPIsService {
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
      
      console.error('Real estate APIs service error:', error);
      throw new Error('Network error');
    }
  }

  // Get real estate properties with optional filtering
  async getRealEstateProperties(filters?: PropertyFilters): Promise<RealEstateAPIResponse> {
    const params = new URLSearchParams();
    
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, value.toString());
        }
      });
    }

    const endpoint = `/api/v1/real-estate-apis/properties${params.toString() ? `?${params.toString()}` : ''}`;
    return this.makeRequest<RealEstateAPIResponse>(endpoint);
  }

  // Get specific property details
  async getPropertyDetail(propertyId: string): Promise<PropertyData> {
    return this.makeRequest<PropertyData>(`/api/v1/real-estate-apis/property/${propertyId}`);
  }

  // Get live market data
  async getMarketData(): Promise<MarketData> {
    return this.makeRequest<MarketData>('/api/v1/real-estate-apis/market-data');
  }

  // Get API status
  async getAPIStatus(): Promise<APIStatus> {
    return this.makeRequest<APIStatus>('/api/v1/real-estate-apis/api-status');
  }

  // Refresh property data
  async refreshPropertyData(): Promise<any> {
    return this.makeRequest<any>('/api/v1/real-estate-apis/refresh-data', {
      method: 'POST'
    });
  }

  // Quick connection test
  async testConnection(): Promise<boolean> {
    try {
      await this.getAPIStatus();
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
        properties: '/api/v1/real-estate-apis/properties',
        propertyDetail: '/api/v1/real-estate-apis/property',
        marketData: '/api/v1/real-estate-apis/market-data',
        apiStatus: '/api/v1/real-estate-apis/api-status',
        refreshData: '/api/v1/real-estate-apis/refresh-data'
      }
    };
  }
}

export const realEstateAPIsService = new RealEstateAPIsService();
export default realEstateAPIsService;
