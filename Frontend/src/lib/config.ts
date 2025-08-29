// Configuration file for the application
export const config = {
  // API Configuration
  api: {
    baseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
    timeout: 30000, // 30 seconds
    retryAttempts: 3,
  },
  
  // Agent Activity Console Configuration
  agentConsole: {
    pollingInterval: 10000, // 10 seconds
    maxActivities: 50,
    connectionCheckInterval: 30000, // 30 seconds
  },
  
  // Feature Flags
  features: {
    realTimeUpdates: false, // WebSocket support
    agentActivityConsole: true,
    dataIntegration: true,
    aiInsights: true,
  },
  
  // UI Configuration
  ui: {
    theme: 'system', // system, light, dark
    animations: true,
    compactMode: false,
  }
};

export default config;
