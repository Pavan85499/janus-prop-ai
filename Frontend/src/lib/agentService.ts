// Agent Service for handling AI Agent API calls
import config from './config';

export interface AgentActivity {
  id: string;
  agent: string;
  message: string;
  status: 'in-progress' | 'completed' | 'alert';
  timestamp: string;
  details: string;
  agent_type?: string;
}

export interface AgentStatus {
  name: string;
  status: string;
  capabilities: string[];
  last_activity: string;
}

export interface AgentActivityResponse {
  activities: AgentActivity[];
  summary: {
    total_activities: number;
    active_tasks: number;
    completed_tasks: number;
    alerts: number;
    system_status: string;
  };
}

export interface AgentsStatusResponse {
  agents: Record<string, AgentStatus>;
  total_agents: number;
  healthy_agents: number;
  timestamp: string;
}

class AgentService {
  private async makeRequest<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), config.api.timeout);

    try {
      const response = await fetch(`${config.api.baseUrl}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
        },
        signal: controller.signal,
        ...options,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
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
      
      console.error('Agent service error:', error);
      throw new Error('Network error');
    }
  }

  async getAgentActivity(limit: number = config.agentConsole.maxActivities, agentType?: string): Promise<AgentActivityResponse> {
    const params = new URLSearchParams();
    if (limit) params.append('limit', limit.toString());
    if (agentType) params.append('agent_type', agentType);

    const endpoint = `/api/v1/agents/activity${params.toString() ? `?${params.toString()}` : ''}`;
    return this.makeRequest<AgentActivityResponse>(endpoint);
  }

  async getAgentsStatus(): Promise<AgentsStatusResponse> {
    return this.makeRequest<AgentsStatusResponse>('/api/v1/agents/status');
  }

  async dismissActivity(activityId: string): Promise<{ success: boolean; message: string }> {
    return this.makeRequest<{ success: boolean; message: string }>('/api/v1/agents/activity/dismiss', {
      method: 'POST',
      body: JSON.stringify({ activity_id: activityId }),
    });
  }

  async getSystemStatus(): Promise<unknown> {
    return this.makeRequest<unknown>('/api/v1/health/detailed');
  }

  // Health check for the backend
  async healthCheck(): Promise<boolean> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout for health check
      
      const response = await fetch(`${config.api.baseUrl}/health`, {
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);
      return response.ok;
    } catch {
      return false;
    }
  }

  // Get API configuration info
  getApiInfo() {
    return {
      baseUrl: config.api.baseUrl,
      timeout: config.api.timeout,
      features: config.features,
    };
  }

  // Gemini AI Methods
  async analyzePropertyWithGemini(propertyData: unknown): Promise<unknown> {
    return this.makeRequest<unknown>('/api/v1/ai-insights/generate', {
      method: 'POST',
      body: JSON.stringify({ property_data: propertyData }),
    });
  }

  async generateInsightsWithGemini(insightType: string, propertyContext: unknown): Promise<unknown> {
    return this.makeRequest<unknown>('/api/v1/ai-insights/insights', {
      method: 'POST',
      body: JSON.stringify({ 
        insight_type: insightType, 
        property_context: propertyContext 
      }),
    });
  }

  async performMarketAnalysisWithGemini(location: string, marketData: unknown): Promise<unknown> {
    return this.makeRequest<unknown>('/api/v1/ai-insights/analyses', {
      method: 'POST',
      body: JSON.stringify({ 
        location, 
        market_data: marketData 
      }),
    });
  }

  // ATTOM Data Methods
  async getATTOMPropertyData(address: string): Promise<unknown> {
    return this.makeRequest<unknown>(`/api/v1/real-estate-apis/property/${encodeURIComponent(address)}`);
  }

  async searchATTOMProperties(criteria: unknown): Promise<unknown> {
    return this.makeRequest<unknown>('/api/v1/real-estate-apis/properties', {
      method: 'POST',
      body: JSON.stringify({ criteria }),
    });
  }

  async getATTOMMarketData(location: string): Promise<unknown> {
    return this.makeRequest<unknown>('/api/v1/real-estate-apis/market-data');
  }

  async getATTOMComparables(propertyData: unknown, radius: number = 0.5, limit: number = 10): Promise<unknown> {
    return this.makeRequest<unknown>('/api/v1/real-estate-apis/properties', {
      method: 'POST',
      body: JSON.stringify({ 
        property_data: propertyData, 
        radius, 
        limit 
      }),
    });
  }

  async getATTOMForeclosureData(location: string): Promise<unknown> {
    return this.makeRequest<unknown>('/api/v1/real-estate-apis/properties');
  }
}

export const agentService = new AgentService();
export default agentService;
