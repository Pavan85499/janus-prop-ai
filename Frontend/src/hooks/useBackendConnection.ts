import { useState, useEffect, useCallback } from 'react';
import backendService, { BackendHealth, BackendStatus } from '../lib/backendService';

export interface BackendConnectionState {
  isConnected: boolean;
  isConnecting: boolean;
  health: BackendHealth | null;
  status: BackendStatus | null;
  lastCheck: Date | null;
  error: string | null;
}

export interface UseBackendConnectionReturn extends BackendConnectionState {
  checkHealth: () => Promise<void>;
  checkDetailedStatus: () => Promise<void>;
  testConnection: () => Promise<boolean>;
  refresh: () => Promise<void>;
}

export function useBackendConnection(
  autoCheck: boolean = true,
  checkInterval: number = 30000 // 30 seconds
): UseBackendConnectionReturn {
  const [state, setState] = useState<BackendConnectionState>({
    isConnected: false,
    isConnecting: false,
    health: null,
    status: null,
    lastCheck: null,
    error: null,
  });

  const checkHealth = useCallback(async () => {
    setState(prev => ({ ...prev, isConnecting: true, error: null }));
    
    try {
      const health = await backendService.healthCheck();
      setState(prev => ({
        ...prev,
        isConnected: true,
        isConnecting: false,
        health,
        lastCheck: new Date(),
        error: null,
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        isConnected: false,
        isConnecting: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      }));
    }
  }, []);

  const checkDetailedStatus = useCallback(async () => {
    if (!state.isConnected) return;
    
    try {
      const status = await backendService.detailedHealthCheck();
      setState(prev => ({
        ...prev,
        status,
        lastCheck: new Date(),
      }));
    } catch (error) {
      console.warn('Failed to get detailed status:', error);
    }
  }, [state.isConnected]);

  const testConnection = useCallback(async (): Promise<boolean> => {
    try {
      const connected = await backendService.testConnection();
      setState(prev => ({
        ...prev,
        isConnected: connected,
        lastCheck: new Date(),
        error: connected ? null : 'Connection test failed',
      }));
      return connected;
    } catch (error) {
      setState(prev => ({
        ...prev,
        isConnected: false,
        error: error instanceof Error ? error.message : 'Connection test failed',
      }));
      return false;
    }
  }, []);

  const refresh = useCallback(async () => {
    await checkHealth();
    if (state.isConnected) {
      await checkDetailedStatus();
    }
  }, [checkHealth, checkDetailedStatus, state.isConnected]);

  // Auto-check on mount and interval
  useEffect(() => {
    if (autoCheck) {
      checkHealth();
      
      const interval = setInterval(checkHealth, checkInterval);
      return () => clearInterval(interval);
    }
  }, [autoCheck, checkInterval, checkHealth]);

  // Auto-refresh detailed status when connected
  useEffect(() => {
    if (state.isConnected && autoCheck) {
      const interval = setInterval(checkDetailedStatus, checkInterval);
      return () => clearInterval(interval);
    }
  }, [state.isConnected, autoCheck, checkInterval, checkDetailedStatus]);

  return {
    ...state,
    checkHealth,
    checkDetailedStatus,
    testConnection,
    refresh,
  };
}
