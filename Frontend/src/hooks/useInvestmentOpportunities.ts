import { useState, useEffect, useCallback, useRef } from 'react';
import investmentOpportunitiesService, { 
  InvestmentOpportunity, 
  InvestmentOpportunityResponse, 
  MarketAnalysis,
  InvestmentFilters 
} from '../lib/investmentOpportunitiesService';

interface UseInvestmentOpportunitiesReturn {
  opportunities: InvestmentOpportunity[];
  marketAnalysis: MarketAnalysis | null;
  summary: any;
  loading: boolean;
  error: string | null;
  isConnected: boolean;
  lastUpdated: Date | null;
  refreshOpportunities: () => Promise<void>;
  refreshMarketAnalysis: () => Promise<void>;
  applyFilters: (filters: InvestmentFilters) => Promise<void>;
  clearFilters: () => Promise<void>;
  testConnection: () => Promise<boolean>;
}

export function useInvestmentOpportunities(
  autoRefresh: boolean = true,
  refreshInterval: number = 60000 // 1 minute
): UseInvestmentOpportunitiesReturn {
  const [opportunities, setOpportunities] = useState<InvestmentOpportunity[]>([]);
  const [marketAnalysis, setMarketAnalysis] = useState<MarketAnalysis | null>(null);
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  
  const refreshIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const mountedRef = useRef(true);
  const currentFiltersRef = useRef<InvestmentFilters>({});

  // Check connection status
  const checkConnection = useCallback(async () => {
    try {
      const connected = await investmentOpportunitiesService.testConnection();
      setIsConnected(connected);
      return connected;
    } catch {
      setIsConnected(false);
      return false;
    }
  }, []);

  // Fetch investment opportunities
  const fetchOpportunities = useCallback(async (filters?: InvestmentFilters) => {
    if (!mountedRef.current) return;
    
    try {
      setError(null);
      const response = await investmentOpportunitiesService.getInvestmentOpportunities(filters);
      setOpportunities(response.opportunities);
      setSummary(response.summary);
      setLastUpdated(new Date(response.last_updated));
      
      // Update current filters
      if (filters) {
        currentFiltersRef.current = filters;
      }
    } catch (err) {
      if (mountedRef.current) {
        setError(err instanceof Error ? err.message : 'Failed to fetch opportunities');
        console.error('Error fetching opportunities:', err);
      }
    }
  }, []);

  // Fetch market analysis
  const fetchMarketAnalysis = useCallback(async () => {
    if (!mountedRef.current) return;
    
    try {
      const analysis = await investmentOpportunitiesService.getMarketAnalysis();
      setMarketAnalysis(analysis);
    } catch (err) {
      if (mountedRef.current) {
        console.error('Error fetching market analysis:', err);
      }
    }
  }, []);

  // Refresh opportunities
  const refreshOpportunities = useCallback(async () => {
    await fetchOpportunities(currentFiltersRef.current);
  }, [fetchOpportunities]);

  // Refresh market analysis
  const refreshMarketAnalysis = useCallback(async () => {
    await fetchMarketAnalysis();
  }, [fetchMarketAnalysis]);

  // Apply filters
  const applyFilters = useCallback(async (filters: InvestmentFilters) => {
    setLoading(true);
    try {
      await fetchOpportunities(filters);
    } finally {
      if (mountedRef.current) {
        setLoading(false);
      }
    }
  }, [fetchOpportunities]);

  // Clear filters
  const clearFilters = useCallback(async () => {
    setLoading(true);
    try {
      currentFiltersRef.current = {};
      await fetchOpportunities();
    } finally {
      if (mountedRef.current) {
        setLoading(false);
      }
    }
  }, [fetchOpportunities]);

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
            await refreshOpportunities();
            await refreshMarketAnalysis();
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
  }, [autoRefresh, isConnected, refreshInterval, refreshOpportunities, refreshMarketAnalysis]);

  // Initial data fetch
  useEffect(() => {
    const initialize = async () => {
      const connected = await checkConnection();
      if (connected) {
        await Promise.all([
          fetchOpportunities(),
          fetchMarketAnalysis()
        ]);
      }
      setLoading(false);
    };

    initialize();

    return () => {
      mountedRef.current = false;
    };
  }, [checkConnection, fetchOpportunities, fetchMarketAnalysis]);

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
    opportunities,
    marketAnalysis,
    summary,
    loading,
    error,
    isConnected,
    lastUpdated,
    refreshOpportunities,
    refreshMarketAnalysis,
    applyFilters,
    clearFilters,
    testConnection,
  };
}
