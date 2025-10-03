import { useState, useEffect, useCallback } from 'react';

interface TimeSlot {
  id: string;
  start_time: string;
  end_time: string;
  is_available: boolean;
  timezone: string;
}

interface DemoAvailability {
  date: string;
  available_slots: TimeSlot[];
  timezone: string;
}

interface DemoRequest {
  id?: string;
  first_name: string;
  last_name: string;
  email: string;
  company?: string;
  phone?: string;
  demo_type: string;
  preferred_date: string;
  preferred_time_slots: string[];
  timezone: string;
  company_size?: string;
  current_solution?: string;
  specific_requirements?: string;
  status?: string;
  created_at?: string;
  updated_at?: string;
}

interface DemoStats {
  total_requests: number;
  status_breakdown: Record<string, number>;
  type_breakdown: Record<string, number>;
  recent_requests: number;
  available_slots: number;
}

interface UseDemoScheduleReturn {
  // Data
  availability: DemoAvailability[];
  demoRequests: DemoRequest[];
  stats: DemoStats | null;
  
  // Loading states
  loadingAvailability: boolean;
  loadingRequests: boolean;
  loadingStats: boolean;
  submitting: boolean;
  
  // Error states
  error: string | null;
  
  // Actions
  loadAvailability: (startDate?: Date, endDate?: Date, timezone?: string) => Promise<void>;
  createDemoRequest: (request: Omit<DemoRequest, 'id' | 'created_at' | 'updated_at'>) => Promise<DemoRequest>;
  getDemoRequests: (status?: string, limit?: number, offset?: number) => Promise<void>;
  getDemoRequest: (id: string) => Promise<DemoRequest>;
  updateDemoRequest: (id: string, updates: Partial<DemoRequest>) => Promise<DemoRequest>;
  cancelDemoRequest: (id: string) => Promise<void>;
  getStats: () => Promise<void>;
  
  // Utility functions
  refreshAvailability: () => Promise<void>;
  refreshRequests: () => Promise<void>;
  refreshStats: () => Promise<void>;
}

const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

export function useDemoSchedule(): UseDemoScheduleReturn {
  const [availability, setAvailability] = useState<DemoAvailability[]>([]);
  const [demoRequests, setDemoRequests] = useState<DemoRequest[]>([]);
  const [stats, setStats] = useState<DemoStats | null>(null);
  
  const [loadingAvailability, setLoadingAvailability] = useState(false);
  const [loadingRequests, setLoadingRequests] = useState(false);
  const [loadingStats, setLoadingStats] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  
  const [error, setError] = useState<string | null>(null);

  // Load availability
  const loadAvailability = useCallback(async (
    startDate?: Date, 
    endDate?: Date, 
    timezone: string = 'UTC'
  ) => {
    try {
      setLoadingAvailability(true);
      setError(null);
      
      const params = new URLSearchParams();
      if (startDate) params.append('start_date', startDate.toISOString());
      if (endDate) params.append('end_date', endDate.toISOString());
      params.append('timezone', timezone);
      
      const response = await fetch(`${API_BASE_URL}/api/v1/demo-schedule/availability?${params}`);
      
      if (!response.ok) {
        throw new Error(`Failed to load availability: ${response.statusText}`);
      }
      
      const data = await response.json();
      setAvailability(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load availability';
      setError(errorMessage);
      console.error('Error loading availability:', err);
    } finally {
      setLoadingAvailability(false);
    }
  }, []);

  // Create demo request
  const createDemoRequest = useCallback(async (request: Omit<DemoRequest, 'id' | 'created_at' | 'updated_at'>): Promise<DemoRequest> => {
    try {
      setSubmitting(true);
      setError(null);
      
      const response = await fetch(`${API_BASE_URL}/api/v1/demo-schedule/request`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Failed to create demo request: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      // Refresh requests list
      await refreshRequests();
      
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create demo request';
      setError(errorMessage);
      console.error('Error creating demo request:', err);
      throw err;
    } finally {
      setSubmitting(false);
    }
  }, []);

  // Get demo requests
  const getDemoRequests = useCallback(async (
    status?: string, 
    limit: number = 50, 
    offset: number = 0
  ) => {
    try {
      setLoadingRequests(true);
      setError(null);
      
      const params = new URLSearchParams();
      if (status) params.append('status', status);
      params.append('limit', limit.toString());
      params.append('offset', offset.toString());
      
      const response = await fetch(`${API_BASE_URL}/api/v1/demo-schedule/requests?${params}`);
      
      if (!response.ok) {
        throw new Error(`Failed to load demo requests: ${response.statusText}`);
      }
      
      const data = await response.json();
      setDemoRequests(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load demo requests';
      setError(errorMessage);
      console.error('Error loading demo requests:', err);
    } finally {
      setLoadingRequests(false);
    }
  }, []);

  // Get single demo request
  const getDemoRequest = useCallback(async (id: string): Promise<DemoRequest> => {
    try {
      setError(null);
      
      const response = await fetch(`${API_BASE_URL}/api/v1/demo-schedule/requests/${id}`);
      
      if (!response.ok) {
        throw new Error(`Failed to load demo request: ${response.statusText}`);
      }
      
      const data = await response.json();
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load demo request';
      setError(errorMessage);
      console.error('Error loading demo request:', err);
      throw err;
    }
  }, []);

  // Update demo request
  const updateDemoRequest = useCallback(async (id: string, updates: Partial<DemoRequest>): Promise<DemoRequest> => {
    try {
      setSubmitting(true);
      setError(null);
      
      const response = await fetch(`${API_BASE_URL}/api/v1/demo-schedule/requests/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updates),
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Failed to update demo request: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      // Update local state
      setDemoRequests(prev => prev.map(req => req.id === id ? data : req));
      
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update demo request';
      setError(errorMessage);
      console.error('Error updating demo request:', err);
      throw err;
    } finally {
      setSubmitting(false);
    }
  }, []);

  // Cancel demo request
  const cancelDemoRequest = useCallback(async (id: string) => {
    try {
      setSubmitting(true);
      setError(null);
      
      const response = await fetch(`${API_BASE_URL}/api/v1/demo-schedule/requests/${id}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Failed to cancel demo request: ${response.statusText}`);
      }
      
      // Update local state
      setDemoRequests(prev => prev.map(req => 
        req.id === id ? { ...req, status: 'cancelled' } : req
      ));
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to cancel demo request';
      setError(errorMessage);
      console.error('Error cancelling demo request:', err);
      throw err;
    } finally {
      setSubmitting(false);
    }
  }, []);

  // Get stats
  const getStats = useCallback(async () => {
    try {
      setLoadingStats(true);
      setError(null);
      
      const response = await fetch(`${API_BASE_URL}/api/v1/demo-schedule/stats`);
      
      if (!response.ok) {
        throw new Error(`Failed to load stats: ${response.statusText}`);
      }
      
      const data = await response.json();
      setStats(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load stats';
      setError(errorMessage);
      console.error('Error loading stats:', err);
    } finally {
      setLoadingStats(false);
    }
  }, []);

  // Refresh functions
  const refreshAvailability = useCallback(() => loadAvailability(), [loadAvailability]);
  const refreshRequests = useCallback(() => getDemoRequests(), [getDemoRequests]);
  const refreshStats = useCallback(() => getStats(), [getStats]);

  // Auto-load availability on mount
  useEffect(() => {
    loadAvailability();
  }, [loadAvailability]);

  return {
    // Data
    availability,
    demoRequests,
    stats,
    
    // Loading states
    loadingAvailability,
    loadingRequests,
    loadingStats,
    submitting,
    
    // Error states
    error,
    
    // Actions
    loadAvailability,
    createDemoRequest,
    getDemoRequests,
    getDemoRequest,
    updateDemoRequest,
    cancelDemoRequest,
    getStats,
    
    // Utility functions
    refreshAvailability,
    refreshRequests,
    refreshStats,
  };
}
