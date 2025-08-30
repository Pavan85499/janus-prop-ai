import { useState, useEffect, useCallback, useRef } from 'react';
import realEstateAPIsService, { 
  PropertyData, 
  RealEstateAPIResponse, 
  MarketData,
  APIStatus,
  PropertyFilters 
} from '../lib/realEstateAPIsService';

interface UseRealEstateAPIsReturn {
  properties: PropertyData[];
  marketData: MarketData | null;
  apiStatus: APIStatus | null;
  summary: any;
  loading: boolean;
  error: string | null;
  isConnected: boolean;
  lastUpdated: Date | null;
  refreshProperties: () => Promise<void>;
  refreshMarketData: () => Promise<void>;
  applyFilters: (filters: PropertyFilters) => Promise<void>;
  clearFilters: () => Promise<void>;
  testConnection: () => Promise<boolean>;
  refreshAPIData: () => Promise<void>;
}

export function useRealEstateAPIs(
  autoRefresh: boolean = true,
  refreshInterval: number = 60000 // 1 minute
): UseRealEstateAPIsReturn {
  const [properties, setProperties] = useState<PropertyData[]>([]);
  const [marketData, setMarketData] = useState<MarketData | null>(null);
  const [apiStatus, setApiStatus] = useState<APIStatus | null>(null);
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  
  const refreshIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const mountedRef = useRef(true);
  const currentFiltersRef = useRef<PropertyFilters>({});

  // Check connection status
  const checkConnection = useCallback(async () => {
    try {
      const connected = await realEstateAPIsService.testConnection();
      setIsConnected(connected);
      return connected;
    } catch {
      setIsConnected(false);
      return false;
    }
  }, []);

  // Fetch real estate properties
  const fetchProperties = useCallback(async (filters?: PropertyFilters) => {
    if (!mountedRef.current) return;
    
    try {
      setError(null);
      const response = await realEstateAPIsService.getRealEstateProperties(filters);
      setProperties(response.properties);
      setSummary(response.summary);
      setLastUpdated(new Date(response.last_updated));
      
      // Update current filters
      if (filters) {
        currentFiltersRef.current = filters;
      }
    } catch (err) {
      if (mountedRef.current) {
        setError(err instanceof Error ? err.message : 'Failed to fetch properties');
        console.error('Error fetching properties:', err);
      }
    }
  }, []);

  // Fetch market data
  const fetchMarketData = useCallback(async () => {
    if (!mountedRef.current) return;
    
    try {
      const data = await realEstateAPIsService.getMarketData();
      setMarketData(data);
    } catch (err) {
      if (mountedRef.current) {
        console.error('Error fetching market data:', err);
      }
    }
  }, []);

  // Fetch API status
  const fetchAPIStatus = useCallback(async () => {
    if (!mountedRef.current) return;
    
    try {
      const status = await realEstateAPIsService.getAPIStatus();
      setApiStatus(status);
    } catch (err) {
      if (mountedRef.current) {
        console.error('Error fetching API status:', err);
      }
    }
  }, []);

  // Refresh properties
  const refreshProperties = useCallback(async () => {
    await fetchProperties(currentFiltersRef.current);
  }, [fetchProperties]);

  // Refresh market data
  const refreshMarketData = useCallback(async () => {
    await fetchMarketData();
  }, [fetchMarketData]);

  // Refresh API data
  const refreshAPIData = useCallback(async () => {
    try {
      await realEstateAPIsService.refreshPropertyData();
      // Wait a bit for the refresh to complete, then fetch updated data
      setTimeout(async () => {
        await Promise.all([
          fetchProperties(currentFiltersRef.current),
          fetchMarketData(),
          fetchAPIStatus()
        ]);
      }, 2000);
    } catch (err) {
      console.error('Error refreshing API data:', err);
    }
  }, [fetchProperties, fetchMarketData, fetchAPIStatus]);

  // Apply filters
  const applyFilters = useCallback(async (filters: PropertyFilters) => {
    setLoading(true);
    try {
      await fetchProperties(filters);
    } finally {
      if (mountedRef.current) {
        setLoading(false);
      }
    }
  }, [fetchProperties]);

  // Clear filters
  const clearFilters = useCallback(async () => {
    setLoading(true);
    try {
      currentFiltersRef.current = {};
      await fetchProperties();
    } finally {
      if (mountedRef.current) {
        setLoading(false);
      }
    }
  }, [fetchProperties]);

  // Test connection
  const testConnection = useCallback(async (): Promise<boolean> => {
    try {
      const connected = await checkConnection();
      return connected;
    } catch (error) {
      console.error('Connection test failed:', error);
      return false;
    }
  }, [checkConnection]);

  // Setup auto-refresh
  useEffect(() => {
    const startAutoRefresh = () => {
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current);
      }
      
      if (autoRefresh && isConnected) {
        refreshIntervalRef.current = setInterval(async () => {
          if (mountedRef.current) {
            await refreshProperties();
            await refreshMarketData();
            await fetchAPIStatus();
          }
        }, refreshInterval);
      }
    };

    if (isConnected) {
      startAutoRefresh();
    }

    return () => {
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current);
      }
    };
  }, [autoRefresh, isConnected, refreshInterval, refreshProperties, refreshMarketData, fetchAPIStatus]);

  // Initial data fetch
  useEffect(() => {
    const initialize = async () => {
      const connected = await checkConnection();
      if (connected) {
        await Promise.all([
          fetchProperties(),
          fetchMarketData(),
          fetchAPIStatus()
        ]);
      }
      setLoading(false);
    };

    initialize();

    return () => {
      mountedRef.current = false;
    };
  }, [checkConnection, fetchProperties, fetchMarketData, fetchAPIStatus]);

  // Periodic connection check
  useEffect(() => {
    const connectionCheckInterval = setInterval(
      checkConnection, 
      30000 // Check every 30 seconds
    );
    
    return () => {
      clearInterval(connectionCheckInterval);
    };
  }, [checkConnection]);

  return {
    properties,
    marketData,
    apiStatus,
    summary,
    loading,
    error,
    isConnected,
    lastUpdated,
    refreshProperties,
    refreshMarketData,
    applyFilters,
    clearFilters,
    testConnection,
    refreshAPIData,
  };
}
