import { useState, useEffect, useCallback, useRef } from 'react';
import { agentService, AgentActivity, AgentActivityResponse, AgentsStatusResponse } from '@/lib/agentService';
import config from '@/lib/config';

interface UseAgentActivityReturn {
  activities: AgentActivity[];
  agentsStatus: AgentsStatusResponse | null;
  loading: boolean;
  error: string | null;
  refreshActivities: () => Promise<void>;
  dismissActivity: (activityId: string) => Promise<void>;
  isBackendConnected: boolean;
}

export const useAgentActivity = (pollingInterval?: number): UseAgentActivityReturn => {
  const [activities, setActivities] = useState<AgentActivity[]>([]);
  const [agentsStatus, setAgentsStatus] = useState<AgentsStatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isBackendConnected, setIsBackendConnected] = useState(false);
  
  const pollingRef = useRef<NodeJS.Timeout | null>(null);
  const mountedRef = useRef(true);

  // Use configured polling interval or fallback to default
  const actualPollingInterval = pollingInterval || config.agentConsole.pollingInterval;

  // Check backend connection
  const checkBackendConnection = useCallback(async () => {
    try {
      const isConnected = await agentService.healthCheck();
      setIsBackendConnected(isConnected);
      return isConnected;
    } catch {
      setIsBackendConnected(false);
      return false;
    }
  }, []);

  // Fetch agent activities
  const fetchActivities = useCallback(async () => {
    if (!mountedRef.current) return;
    
    try {
      setError(null);
      const response = await agentService.getAgentActivity(config.agentConsole.maxActivities);
      setActivities(response.activities);
    } catch (err) {
      if (mountedRef.current) {
        setError(err instanceof Error ? err.message : 'Failed to fetch activities');
        console.error('Error fetching activities:', err);
      }
    }
  }, []);

  // Fetch agents status
  const fetchAgentsStatus = useCallback(async () => {
    if (!mountedRef.current) return;
    
    try {
      const response = await agentService.getAgentsStatus();
      setAgentsStatus(response);
    } catch (err) {
      if (mountedRef.current) {
        console.error('Error fetching agents status:', err);
      }
    }
  }, []);

  // Refresh all data
  const refreshActivities = useCallback(async () => {
    setLoading(true);
    try {
      await Promise.all([fetchActivities(), fetchAgentsStatus()]);
    } finally {
      if (mountedRef.current) {
        setLoading(false);
      }
    }
  }, [fetchActivities, fetchAgentsStatus]);

  // Dismiss activity
  const dismissActivity = useCallback(async (activityId: string) => {
    try {
      await agentService.dismissActivity(activityId);
      // Remove the dismissed activity from local state
      setActivities(prev => prev.filter(activity => activity.id !== activityId));
    } catch (err) {
      console.error('Error dismissing activity:', err);
      // You might want to show a toast notification here
    }
  }, []);

  // Setup polling
  useEffect(() => {
    const startPolling = () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
      }
      
      pollingRef.current = setInterval(async () => {
        if (mountedRef.current && isBackendConnected) {
          await fetchActivities();
          await fetchAgentsStatus();
        }
      }, actualPollingInterval);
    };

    if (isBackendConnected) {
      startPolling();
    }

    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
      }
    };
  }, [isBackendConnected, actualPollingInterval, fetchActivities, fetchAgentsStatus]);

  // Initial data fetch
  useEffect(() => {
    const initialize = async () => {
      const isConnected = await checkBackendConnection();
      if (isConnected) {
        await refreshActivities();
      } else {
        setLoading(false);
      }
    };

    initialize();

    return () => {
      mountedRef.current = false;
    };
  }, [checkBackendConnection, refreshActivities]);

  // Periodic connection check
  useEffect(() => {
    const connectionCheckInterval = setInterval(
      checkBackendConnection, 
      config.agentConsole.connectionCheckInterval
    );
    
    return () => {
      clearInterval(connectionCheckInterval);
    };
  }, [checkBackendConnection]);

  return {
    activities,
    agentsStatus,
    loading,
    error,
    refreshActivities,
    dismissActivity,
    isBackendConnected,
  };
};
