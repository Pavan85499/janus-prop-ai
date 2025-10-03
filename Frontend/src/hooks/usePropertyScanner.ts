import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Types
export interface PropertyScan {
  id: number;
  name: string;
  description?: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  created_at: string;
  started_at?: string;
  completed_at?: string;
  search_criteria: ScanCriteria;
  max_properties: number;
  scan_radius_miles: number;
  total_scanned: number;
  properties_found: number;
  high_potential_count: number;
  distressed_count: number;
  undervalued_count: number;
  user_id: number;
}

export interface ScannedProperty {
  id: number;
  address: string;
  city?: string;
  state?: string;
  zip_code?: string;
  property_type?: string;
  bedrooms?: number;
  bathrooms?: number;
  square_feet?: number;
  list_price?: number;
  estimated_value?: number;
  price_per_sqft?: number;
  investment_potential?: string;
  roi_estimate?: number;
  cap_rate?: number;
  is_distressed: boolean;
  is_undervalued: boolean;
  is_foreclosure: boolean;
  ai_confidence_score?: number;
  ai_analysis?: string;
  scanned_at: string;
}

export interface ScanCriteria {
  city?: string;
  state?: string;
  zip_codes?: string[];
  latitude?: number;
  longitude?: number;
  radius_miles?: number;
  property_types?: string[];
  min_price?: number;
  max_price?: number;
  min_sqft?: number;
  max_sqft?: number;
  min_bedrooms?: number;
  max_bedrooms?: number;
  min_bathrooms?: number;
  max_bathrooms?: number;
  min_lot_size?: number;
  max_lot_size?: number;
  year_built_min?: number;
  year_built_max?: number;
  min_roi?: number;
  max_roi?: number;
  min_cap_rate?: number;
  max_cap_rate?: number;
  min_cash_flow?: number;
  max_cash_flow?: number;
  include_distressed?: boolean;
  include_foreclosures?: boolean;
  include_short_sales?: boolean;
  include_bank_owned?: boolean;
  min_days_on_market?: number;
  max_days_on_market?: number;
  max_price_reductions?: number;
  market_trends?: string[];
  min_appreciation_potential?: number;
  max_appreciation_potential?: number;
  min_ai_confidence?: number;
  investment_potential_levels?: string[];
}

export interface ScanProgress {
  scan_id: number;
  status: string;
  total_properties: number;
  scanned_count: number;
  found_count: number;
  progress_percentage: number;
  estimated_completion?: string;
  current_location?: string;
  errors?: string[];
}

export interface CreateScanRequest {
  name: string;
  description?: string;
  search_criteria: ScanCriteria;
  max_properties: number;
  scan_radius_miles: number;
}

// API functions
const createScan = async (scanData: CreateScanRequest): Promise<PropertyScan> => {
  const response = await fetch(`${API_BASE_URL}/api/v1/property-scanner/scans`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(scanData),
  });

  if (!response.ok) {
    throw new Error('Failed to create scan');
  }

  return response.json();
};

const getScans = async (): Promise<PropertyScan[]> => {
  const response = await fetch(`${API_BASE_URL}/api/v1/property-scanner/scans`);

  if (!response.ok) {
    throw new Error('Failed to fetch scans');
  }

  return response.json();
};

const getScan = async (scanId: number): Promise<PropertyScan> => {
  const response = await fetch(`${API_BASE_URL}/api/v1/property-scanner/scans/${scanId}`);

  if (!response.ok) {
    throw new Error('Failed to fetch scan');
  }

  return response.json();
};

const getScanProgress = async (scanId: number): Promise<ScanProgress> => {
  const response = await fetch(`${API_BASE_URL}/api/v1/property-scanner/scans/${scanId}/progress`);

  if (!response.ok) {
    throw new Error('Failed to fetch scan progress');
  }

  return response.json();
};

const getScannedProperties = async (
  scanId: number,
  filters: {
    skip?: number;
    limit?: number;
    investment_potential?: string;
    is_distressed?: boolean;
    is_undervalued?: boolean;
    min_roi?: number;
    max_roi?: number;
  } = {}
): Promise<ScannedProperty[]> => {
  const params = new URLSearchParams();
  
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      params.append(key, value.toString());
    }
  });

  const response = await fetch(
    `${API_BASE_URL}/api/v1/property-scanner/scans/${scanId}/properties?${params}`
  );

  if (!response.ok) {
    throw new Error('Failed to fetch scanned properties');
  }

  return response.json();
};

const cancelScan = async (scanId: number): Promise<void> => {
  const response = await fetch(`${API_BASE_URL}/api/v1/property-scanner/scans/${scanId}/cancel`, {
    method: 'POST',
  });

  if (!response.ok) {
    throw new Error('Failed to cancel scan');
  }
};

const deleteScan = async (scanId: number): Promise<void> => {
  const response = await fetch(`${API_BASE_URL}/api/v1/property-scanner/scans/${scanId}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    throw new Error('Failed to delete scan');
  }
};

const exportScanResults = async (scanId: number, format: string = 'json'): Promise<unknown> => {
  const response = await fetch(`${API_BASE_URL}/api/v1/property-scanner/scans/${scanId}/export?format=${format}`);

  if (!response.ok) {
    throw new Error('Failed to export scan results');
  }

  return response.json();
};

// React hooks
export const usePropertyScans = () => {
  return useQuery({
    queryKey: ['property-scans'],
    queryFn: getScans,
    refetchInterval: 5000, // Refetch every 5 seconds to get real-time updates
  });
};

export const usePropertyScan = (scanId: number) => {
  return useQuery({
    queryKey: ['property-scan', scanId],
    queryFn: () => getScan(scanId),
    enabled: !!scanId,
  });
};

export const useScanProgress = (scanId: number, enabled: boolean = true) => {
  return useQuery({
    queryKey: ['scan-progress', scanId],
    queryFn: () => getScanProgress(scanId),
    enabled: enabled && !!scanId,
    refetchInterval: 2000, // Refetch every 2 seconds for real-time progress
  });
};

export const useScannedProperties = (
  scanId: number,
  filters: {
    skip?: number;
    limit?: number;
    investment_potential?: string;
    is_distressed?: boolean;
    is_undervalued?: boolean;
    min_roi?: number;
    max_roi?: number;
  } = {}
) => {
  return useQuery({
    queryKey: ['scanned-properties', scanId, filters],
    queryFn: () => getScannedProperties(scanId, filters),
    enabled: !!scanId,
  });
};

export const useCreateScan = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createScan,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['property-scans'] });
    },
  });
};

export const useCancelScan = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: cancelScan,
    onSuccess: (_, scanId) => {
      queryClient.invalidateQueries({ queryKey: ['property-scans'] });
      queryClient.invalidateQueries({ queryKey: ['property-scan', scanId] });
      queryClient.invalidateQueries({ queryKey: ['scan-progress', scanId] });
    },
  });
};

export const useDeleteScan = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteScan,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['property-scans'] });
    },
  });
};

export const useExportScanResults = () => {
  return useMutation({
    mutationFn: ({ scanId, format }: { scanId: number; format?: string }) =>
      exportScanResults(scanId, format),
  });
};

// Custom hook for real-time scan monitoring
export const useRealTimeScanMonitoring = (scanId: number) => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  useEffect(() => {
    if (!scanId) return;

    // In production, this would use WebSocket or Server-Sent Events
    // For now, we'll use polling with the existing query
    const interval = setInterval(() => {
      setLastUpdate(new Date());
    }, 2000);

    return () => clearInterval(interval);
  }, [scanId]);

  return {
    isConnected,
    lastUpdate,
  };
};

// Utility functions
export const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
};

export const formatPercentage = (value: number, decimals: number = 1): string => {
  return `${value.toFixed(decimals)}%`;
};

export const getInvestmentPotentialColor = (potential: string): string => {
  const colors = {
    very_high: 'text-green-600',
    high: 'text-green-500',
    medium: 'text-yellow-600',
    low: 'text-red-600',
  };
  return colors[potential as keyof typeof colors] || 'text-gray-600';
};

export const getStatusColor = (status: string): string => {
  const colors = {
    pending: 'text-yellow-600',
    running: 'text-blue-600',
    completed: 'text-green-600',
    failed: 'text-red-600',
    cancelled: 'text-gray-600',
  };
  return colors[status as keyof typeof colors] || 'text-gray-600';
};
