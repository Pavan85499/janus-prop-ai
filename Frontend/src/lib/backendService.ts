// Backend Service for handling all API communication
import config from './config';

export interface BackendHealth {
  status: string;
  timestamp: string;
  version: string;
  uptime: number;
  services: Record<string, string>;
}

export interface BackendStatus {
  overall_status: string;
  database: string;
  redis: string;
  websocket: string;
  agents: string;
  timestamp: string;
}

export interface SupabaseConfig {
  url: string;
  anon_key: string;
  project_id: string;
  enabled: boolean;
}

export interface SupabaseStatus {
  enabled: boolean;
  connected: boolean;
  project_id: string;
  url: string;
}

class BackendService {
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
      
      console.error('Backend service error:', error);
      throw new Error('Network error');
    }
  }

  // Health and Status
  async healthCheck(): Promise<BackendHealth> {
    return this.makeRequest<BackendHealth>('/health');
  }

  async detailedHealthCheck(): Promise<BackendStatus> {
    return this.makeRequest<BackendStatus>('/api/v1/health/detailed');
  }

  // Supabase Configuration
  async getSupabaseConfig(): Promise<SupabaseConfig> {
    return this.makeRequest<SupabaseConfig>('/api/v1/supabase/config');
  }

  async getSupabaseStatus(): Promise<SupabaseStatus> {
    return this.makeRequest<SupabaseStatus>('/api/v1/supabase/status');
  }

  async testSupabaseConnection(): Promise<{ status: string; message: string }> {
    return this.makeRequest<{ status: string; message: string }>(
      '/api/v1/supabase/test-connection',
      { method: 'POST' }
    );
  }

  // Quick Connection Test
  async testConnection(): Promise<boolean> {
    try {
      await this.healthCheck();
      return true;
    } catch {
      return false;
    }
  }

  // Get Backend Info
  getBackendInfo() {
    return {
      baseUrl: this.baseUrl,
      timeout: this.timeout,
      status: 'disconnected' as const,
    };
  }

  // Update Base URL (for dynamic configuration)
  updateBaseUrl(newUrl: string) {
    this.baseUrl = newUrl;
    config.api.baseUrl = newUrl;
  }

  // Analytics
  async getROITrends(months: number = 12): Promise<{ series: { period: string; avg_roi: number; count: number }[]; unit: string }>{
    return this.makeRequest(`/api/v1/analytics/roi-trends?months=${months}`);
  }

  async getDealVelocity(months: number = 12): Promise<{ series: { period: string; avg_days_to_close: number; count: number }[]; unit: string }>{
    return this.makeRequest(`/api/v1/analytics/deal-velocity?months=${months}`);
  }

  async getPortfolioBreakdown(by: 'type' | 'location' = 'type', topN: number = 10): Promise<{
    by: 'type' | 'location';
    items: { label: string; count: number; total_value: number; share: number }[];
    total_count: number;
    total_value: number;
  }>{
    return this.makeRequest(`/api/v1/analytics/portfolio-breakdown?by=${by}&top_n=${topN}`);
  }
}

export const backendService = new BackendService();
export default backendService;
