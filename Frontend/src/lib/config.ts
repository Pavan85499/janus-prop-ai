// Configuration file for the application
type BooleanLike = boolean | string | undefined | null;

function toBoolean(value: BooleanLike, fallback: boolean = false): boolean {
  if (typeof value === 'boolean') return value;
  if (typeof value === 'string') return value.toLowerCase() === 'true';
  return fallback;
}

function toNumber(value: string | undefined, fallback: number): number {
  const parsed = Number(value);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}

export const config = {
  // API Configuration
  api: {
    baseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
    timeout: toNumber(import.meta.env.VITE_API_TIMEOUT, 30000),
    retryAttempts: toNumber(import.meta.env.VITE_API_RETRY_ATTEMPTS, 3),
    version: import.meta.env.VITE_API_VERSION || 'v1',
  },

  // Websocket / realtime
  websocket: {
    url:
      import.meta.env.VITE_WEBSOCKET_URL ||
      (import.meta.env.VITE_API_BASE_URL
        ? `${String(import.meta.env.VITE_API_BASE_URL).replace('http', 'ws')}/ws`
        : 'ws://localhost:8000/ws'),
    reconnectInterval: toNumber(import.meta.env.VITE_WEBSOCKET_RECONNECT_INTERVAL, 5000),
    maxReconnectAttempts: toNumber(import.meta.env.VITE_WEBSOCKET_MAX_RECONNECT_ATTEMPTS, 5),
    realtimeUpdateInterval: toNumber(import.meta.env.VITE_REALTIME_UPDATE_INTERVAL, 5000),
  },

  // Supabase
  supabase: {
    url: import.meta.env.VITE_SUPABASE_URL || '',
    anonKey:
      import.meta.env.VITE_SUPABASE_ANON_KEY ||
      import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY ||
      '',
    projectId: import.meta.env.VITE_SUPABASE_PROJECT_ID || '',
    enabled: Boolean(import.meta.env.VITE_SUPABASE_URL && (import.meta.env.VITE_SUPABASE_ANON_KEY || import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY)),
  },

  // Agent Activity Console Configuration
  agentConsole: {
    pollingInterval: toNumber(import.meta.env.VITE_AGENT_POLLING_INTERVAL, 10000),
    maxActivities: toNumber(import.meta.env.VITE_AGENT_MAX_ACTIVITIES, 50),
    connectionCheckInterval: toNumber(import.meta.env.VITE_AGENT_CONNECTION_CHECK_INTERVAL, 30000),
  },

  // Feature Flags
  features: {
    realTimeUpdates: toBoolean(import.meta.env.VITE_ENABLE_REAL_TIME_UPDATES, true),
    agentActivityConsole: toBoolean(import.meta.env.VITE_ENABLE_AGENT_CONSOLE, true),
    aiFeatures: toBoolean(import.meta.env.VITE_ENABLE_AI_FEATURES, true),
    propertyAnalysis: toBoolean(import.meta.env.VITE_ENABLE_PROPERTY_ANALYSIS, true),
    marketInsights: toBoolean(import.meta.env.VITE_ENABLE_MARKET_INSIGHTS, true),
    predictiveModeling: toBoolean(import.meta.env.VITE_ENABLE_PREDICTIVE_MODELING, true),
    dataIntegration: toBoolean(import.meta.env.VITE_ENABLE_DATA_INTEGRATION, true),
    aiInsights: toBoolean(import.meta.env.VITE_ENABLE_AI_INSIGHTS, true),
  },

  // UI Configuration
  ui: {
    theme: (import.meta.env.VITE_THEME as 'system' | 'light' | 'dark') || 'system',
    animations: toBoolean(import.meta.env.VITE_ANIMATIONS, true),
    compactMode: toBoolean(import.meta.env.VITE_COMPACT_MODE, false),
  },
} as const;

export default config;
