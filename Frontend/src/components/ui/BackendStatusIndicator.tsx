import React from 'react';
import { useBackendConnection } from '../../hooks/useBackendConnection';
import { Badge } from './badge';
import { Button } from './button';
import { Card, CardContent, CardHeader, CardTitle } from './card';
import { 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  RefreshCw, 
  Server,
  Database,
  Wifi,
  Activity
} from 'lucide-react';

interface BackendStatusIndicatorProps {
  showDetails?: boolean;
  className?: string;
}

export function BackendStatusIndicator({ 
  showDetails = false, 
  className = '' 
}: BackendStatusIndicatorProps) {
  const {
    isConnected,
    isConnecting,
    health,
    status,
    lastCheck,
    error,
    checkHealth,
    testConnection,
    refresh
  } = useBackendConnection(true, 30000);

  const getStatusIcon = () => {
    if (isConnecting) return <RefreshCw className="h-4 w-4 animate-spin" />;
    if (isConnected) return <CheckCircle className="h-4 w-4 text-green-500" />;
    return <XCircle className="h-4 w-4 text-red-500" />;
  };

  const getStatusColor = () => {
    if (isConnecting) return 'bg-yellow-100 text-yellow-800';
    if (isConnected) return 'bg-green-100 text-green-800';
    return 'bg-red-100 text-red-800';
  };

  const getStatusText = () => {
    if (isConnecting) return 'Connecting...';
    if (isConnected) return 'Connected';
    return 'Disconnected';
  };

  const formatTimestamp = (date: Date | null) => {
    if (!date) return 'Never';
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }).format(date);
  };

  const handleRefresh = async () => {
    await refresh();
  };

  const handleTestConnection = async () => {
    await testConnection();
  };

  if (!showDetails) {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        <Server className="h-4 w-4" />
        <Badge variant={isConnected ? "default" : "destructive"}>
          {getStatusText()}
        </Badge>
        {error && (
          <span className="text-xs text-red-600 truncate max-w-32">
            {error}
          </span>
        )}
      </div>
    );
  }

  return (
    <Card className={className}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Server className="h-5 w-5" />
          Backend Status
          <Badge variant={isConnected ? "default" : "destructive"}>
            {getStatusText()}
          </Badge>
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Connection Status */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {getStatusIcon()}
            <span className="font-medium">Connection</span>
          </div>
          <div className="flex gap-2">
            <Button
              size="sm"
              variant="outline"
              onClick={handleTestConnection}
              disabled={isConnecting}
            >
              Test
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={handleRefresh}
              disabled={isConnecting}
            >
              <RefreshCw className={`h-4 w-4 ${isConnecting ? 'animate-spin' : ''}`} />
            </Button>
          </div>
        </div>

        {/* Last Check */}
        <div className="text-sm text-gray-600">
          Last check: {formatTimestamp(lastCheck)}
        </div>

        {/* Error Display */}
        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-md">
            <div className="flex items-center gap-2 text-red-800">
              <AlertCircle className="h-4 w-4" />
              <span className="font-medium">Error:</span>
            </div>
            <p className="text-sm text-red-700 mt-1">{error}</p>
          </div>
        )}

        {/* Health Status */}
        {health && (
          <div className="space-y-3">
            <h4 className="font-medium flex items-center gap-2">
              <Activity className="h-4 w-4" />
              System Health
            </h4>
            
            <div className="grid grid-cols-2 gap-3">
              <div className="flex items-center gap-2">
                <Database className="h-4 w-4" />
                <span className="text-sm">Database:</span>
                <Badge 
                  variant={health.services.database === 'healthy' ? 'default' : 'destructive'}
                  className="text-xs"
                >
                  {health.services.database}
                </Badge>
              </div>
              
              <div className="flex items-center gap-2">
                <Wifi className="h-4 w-4" />
                <span className="text-sm">Redis:</span>
                <Badge 
                  variant={health.services.redis === 'healthy' ? 'default' : 'destructive'}
                  className="text-xs"
                >
                  {health.services.redis}
                </Badge>
              </div>
            </div>

            <div className="text-xs text-gray-600">
              Version: {health.version} | Uptime: {health.uptime}s
            </div>
          </div>
        )}

        {/* Detailed Status */}
        {status && (
          <div className="space-y-3">
            <h4 className="font-medium flex items-center gap-2">
              <Server className="h-4 w-4" />
              Detailed Status
            </h4>
            
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <span className="font-medium">Overall:</span>
                <Badge 
                  variant={status.overall_status === 'healthy' ? 'default' : 'destructive'}
                  className="ml-2 text-xs"
                >
                  {status.overall_status}
                </Badge>
              </div>
              
              <div>
                <span className="font-medium">Agents:</span>
                <Badge 
                  variant={status.agents === 'healthy' ? 'default' : 'destructive'}
                  className="ml-2 text-xs"
                >
                  {status.agents}
                </Badge>
              </div>
            </div>
          </div>
        )}

        {/* Connection Info */}
        <div className="pt-2 border-t">
          <div className="text-xs text-gray-600">
            <div>Base URL: {health?.timestamp ? 'Connected' : 'Not configured'}</div>
            <div>API Timeout: 30s</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
