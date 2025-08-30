import React, { useState } from 'react';
import { BackendStatusIndicator } from '../components/ui/BackendStatusIndicator';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { 
  Server, 
  Activity, 
  Database, 
  Wifi, 
  TestTube,
  CheckCircle,
  XCircle,
  AlertCircle
} from 'lucide-react';
import backendService from '../lib/backendService';

export default function BackendTest() {
  const [testResults, setTestResults] = useState<Record<string, any>>({});
  const [isTesting, setIsTesting] = useState(false);

  const runTest = async (testName: string, testFn: () => Promise<any>) => {
    setTestResults(prev => ({ ...prev, [testName]: { status: 'running' } }));
    
    try {
      const result = await testFn();
      setTestResults(prev => ({ 
        ...prev, 
        [testName]: { status: 'success', result } 
      }));
    } catch (error) {
      setTestResults(prev => ({ 
        ...prev, 
        [testName]: { 
          status: 'error', 
          error: error instanceof Error ? error.message : 'Unknown error' 
        } 
      }));
    }
  };

  const runAllTests = async () => {
    setIsTesting(true);
    
    // Health check
    await runTest('Health Check', () => backendService.healthCheck());
    
    // Detailed health
    await runTest('Detailed Health', () => backendService.detailedHealthCheck());
    
    // Supabase config
    await runTest('Supabase Config', () => backendService.getSupabaseConfig());
    
    // Supabase status
    await runTest('Supabase Status', () => backendService.getSupabaseStatus());
    
    // Connection test
    await runTest('Connection Test', () => backendService.testConnection());
    
    setIsTesting(false);
  };

  const getTestStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'error': return <XCircle className="h-4 w-4 text-red-500" />;
      case 'running': return <Activity className="h-4 w-4 text-blue-500 animate-pulse" />;
      default: return <AlertCircle className="h-4 w-4 text-gray-500" />;
    }
  };

  const getTestStatusBadge = (status: string) => {
    switch (status) {
      case 'success': return <Badge variant="default">Success</Badge>;
      case 'error': return <Badge variant="destructive">Error</Badge>;
      case 'running': return <Badge variant="secondary">Running</Badge>;
      default: return <Badge variant="outline">Not Run</Badge>;
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold flex items-center justify-center gap-2">
          <Server className="h-8 w-8" />
          Backend Connection Test
        </h1>
        <p className="text-gray-600 mt-2">
          Test and verify your backend connection, health status, and API endpoints
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Backend Status */}
        <div className="lg:col-span-1">
          <BackendStatusIndicator showDetails={true} />
        </div>

        {/* Test Controls */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TestTube className="h-5 w-5" />
                Test Controls
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2">
                <Button 
                  onClick={runAllTests} 
                  disabled={isTesting}
                  className="flex-1"
                >
                  {isTesting ? 'Running Tests...' : 'Run All Tests'}
                </Button>
                <Button 
                  variant="outline" 
                  onClick={() => setTestResults({})}
                >
                  Clear Results
                </Button>
              </div>
              
              <div className="text-sm text-gray-600">
                <p>• Health Check: Basic backend health status</p>
                <p>• Detailed Health: Comprehensive system status</p>
                <p>• Supabase Config: Database configuration</p>
                <p>• Supabase Status: Database connection status</p>
                <p>• Connection Test: Quick connectivity test</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Test Results */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Test Results
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="all" className="w-full">
            <TabsList className="grid w-full grid-cols-6">
              <TabsTrigger value="all">All</TabsTrigger>
              <TabsTrigger value="health">Health</TabsTrigger>
              <TabsTrigger value="supabase">Supabase</TabsTrigger>
              <TabsTrigger value="connection">Connection</TabsTrigger>
              <TabsTrigger value="raw">Raw Data</TabsTrigger>
            </TabsList>

            <TabsContent value="all" className="space-y-4">
              {Object.entries(testResults).map(([testName, result]) => (
                <div key={testName} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium">{testName}</h3>
                    <div className="flex items-center gap-2">
                      {getTestStatusIcon(result.status)}
                      {getTestStatusBadge(result.status)}
                    </div>
                  </div>
                  
                  {result.status === 'success' && (
                    <div className="text-sm text-gray-600">
                      <pre className="bg-gray-50 p-2 rounded text-xs overflow-x-auto">
                        {JSON.stringify(result.result, null, 2)}
                      </pre>
                    </div>
                  )}
                  
                  {result.status === 'error' && (
                    <div className="text-sm text-red-600">
                      Error: {result.error}
                    </div>
                  )}
                </div>
              ))}
            </TabsContent>

            <TabsContent value="health" className="space-y-4">
              {Object.entries(testResults)
                .filter(([name]) => name.includes('Health'))
                .map(([testName, result]) => (
                  <div key={testName} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-medium">{testName}</h3>
                      <div className="flex items-center gap-2">
                        {getTestStatusIcon(result.status)}
                        {getTestStatusBadge(result.status)}
                      </div>
                    </div>
                    
                    {result.status === 'success' && (
                      <div className="text-sm text-gray-600">
                        <pre className="bg-gray-50 p-2 rounded text-xs overflow-x-auto">
                          {JSON.stringify(result.result, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                ))}
            </TabsContent>

            <TabsContent value="supabase" className="space-y-4">
              {Object.entries(testResults)
                .filter(([name]) => name.includes('Supabase'))
                .map(([testName, result]) => (
                  <div key={testName} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-medium">{testName}</h3>
                      <div className="flex items-center gap-2">
                        {getTestStatusIcon(result.status)}
                        {getTestStatusBadge(result.status)}
                      </div>
                    </div>
                    
                    {result.status === 'success' && (
                      <div className="text-sm text-gray-600">
                        <pre className="bg-gray-50 p-2 rounded text-xs overflow-x-auto">
                          {JSON.stringify(result.result, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                ))}
            </TabsContent>

            <TabsContent value="connection" className="space-y-4">
              {Object.entries(testResults)
                .filter(([name]) => name.includes('Connection'))
                .map(([testName, result]) => (
                  <div key={testName} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-medium">{testName}</h3>
                      <div className="flex items-center gap-2">
                        {getTestStatusIcon(result.status)}
                        {getTestStatusBadge(result.status)}
                      </div>
                    </div>
                    
                    {result.status === 'success' && (
                      <div className="text-sm text-gray-600">
                        <pre className="bg-gray-50 p-2 rounded text-xs overflow-x-auto">
                          {JSON.stringify(result.result, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                ))}
            </TabsContent>

            <TabsContent value="raw" className="space-y-4">
              <div className="border rounded-lg p-4">
                <h3 className="font-medium mb-2">All Test Results (Raw)</h3>
                <pre className="bg-gray-50 p-4 rounded text-xs overflow-x-auto">
                  {JSON.stringify(testResults, null, 2)}
                </pre>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Connection Info */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Server className="h-5 w-5" />
            Connection Information
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 className="font-medium mb-2">Backend Service</h4>
              <div className="space-y-2 text-sm">
                <div>Base URL: {backendService.getBackendInfo().baseUrl}</div>
                <div>Timeout: {backendService.getBackendInfo().timeout}ms</div>
                <div>Status: {backendService.getBackendInfo().status}</div>
              </div>
            </div>
            
            <div>
              <h4 className="font-medium mb-2">Environment</h4>
              <div className="space-y-2 text-sm">
                <div>Node Env: {import.meta.env.MODE}</div>
                <div>API Base: {import.meta.env.VITE_API_BASE_URL || 'Not set'}</div>
                <div>Supabase URL: {import.meta.env.VITE_SUPABASE_URL || 'Not set'}</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
