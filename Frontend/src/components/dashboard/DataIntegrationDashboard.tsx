import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { 
  Database, 
  RefreshCw, 
  CheckCircle, 
  AlertTriangle, 
  XCircle,
  Plus,
  Settings,
  BarChart3,
  Clock,
  Activity
} from 'lucide-react';

interface DataSource {
  source_id: string;
  name: string;
  type: string;
  status: string;
  last_sync: string | null;
  record_count: number;
  sync_status: string;
  error_count: number;
}

interface DataIntegrationStats {
  total_properties: number;
  properties_today: number;
  sync_success_rate: number;
  active_sources: number;
  last_full_sync: string;
}

interface DataIntegrationDashboardProps {
  onSyncSource: (sourceId: string) => void;
  onAddSource: (sourceConfig: any) => void;
}

const DataIntegrationDashboard: React.FC<DataIntegrationDashboardProps> = ({ 
  onSyncSource, 
  onAddSource 
}) => {
  const [dataSources, setDataSources] = useState<DataSource[]>([
    {
      source_id: "realie_api",
      name: "Realie API",
      type: "api",
      status: "active",
      last_sync: "2024-01-15T10:30:00Z",
      record_count: 15420,
      sync_status: "success",
      error_count: 0
    },
    {
      source_id: "attom_data",
      name: "ATTOM Data",
      type: "api",
      status: "inactive",
      last_sync: null,
      record_count: 0,
      sync_status: "pending",
      error_count: 0
    }
  ]);

  const [stats, setStats] = useState<DataIntegrationStats>({
    total_properties: 15420,
    properties_today: 127,
    sync_success_rate: 98.5,
    active_sources: 1,
    last_full_sync: "2024-01-15T10:30:00Z"
  });

  const [showAddSource, setShowAddSource] = useState(false);
  const [newSource, setNewSource] = useState({
    name: '',
    type: 'api',
    base_url: '',
    api_key: ''
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800 border-green-200';
      case 'inactive': return 'bg-gray-100 text-gray-800 border-gray-200';
      case 'error': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getSyncStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'pending': return <Clock className="h-4 w-4 text-yellow-600" />;
      case 'error': return <XCircle className="h-4 w-4 text-red-600" />;
      default: return <Clock className="h-4 w-4 text-gray-600" />;
    }
  };

  const handleSyncSource = (sourceId: string) => {
    onSyncSource(sourceId);
    // Update local state to show syncing
    setDataSources(prev => prev.map(source => 
      source.source_id === sourceId 
        ? { ...source, sync_status: 'pending' }
        : source
    ));
  };

  const handleAddSource = () => {
    if (newSource.name && newSource.base_url) {
      const sourceConfig = {
        source_id: newSource.name.toLowerCase().replace(/\s+/g, '_'),
        ...newSource
      };
      onAddSource(sourceConfig);
      
      // Add to local state
      const newDataSource: DataSource = {
        source_id: sourceConfig.source_id,
        name: newSource.name,
        type: newSource.type,
        status: 'inactive',
        last_sync: null,
        record_count: 0,
        sync_status: 'pending',
        error_count: 0
      };
      
      setDataSources(prev => [...prev, newDataSource]);
      setStats(prev => ({ ...prev, active_sources: prev.active_sources + 1 }));
      
      // Reset form
      setNewSource({ name: '', type: 'api', base_url: '', api_key: '' });
      setShowAddSource(false);
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleString();
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat().format(num);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Data Integration Dashboard</h2>
          <p className="text-gray-600">Monitor and manage your property data sources</p>
        </div>
        <Button onClick={() => setShowAddSource(true)} className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Add Data Source
        </Button>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Properties</p>
                <p className="text-2xl font-bold text-gray-900">{formatNumber(stats.total_properties)}</p>
              </div>
              <Database className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Properties Today</p>
                <p className="text-2xl font-bold text-gray-900">{formatNumber(stats.properties_today)}</p>
              </div>
              <Activity className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Sync Success Rate</p>
                <p className="text-2xl font-bold text-gray-900">{stats.sync_success_rate}%</p>
              </div>
              <BarChart3 className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Sources</p>
                <p className="text-2xl font-bold text-gray-900">{stats.active_sources}</p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Data Sources */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            Data Sources
          </CardTitle>
          <CardDescription>
            Manage your property data sources and monitor sync status
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {dataSources.map((source) => (
              <div key={source.source_id} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="flex items-center gap-2">
                      {getSyncStatusIcon(source.sync_status)}
                      <h3 className="font-semibold text-gray-900">{source.name}</h3>
                    </div>
                    <Badge variant="outline" className={getStatusColor(source.status)}>
                      {source.status}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleSyncSource(source.source_id)}
                      disabled={source.sync_status === 'pending'}
                    >
                      <RefreshCw className={`h-4 w-4 mr-2 ${source.sync_status === 'pending' ? 'animate-spin' : ''}`} />
                      Sync
                    </Button>
                    <Button variant="ghost" size="sm">
                      <Settings className="h-4 w-4" />
                    </Button>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <p className="text-gray-600">Type</p>
                    <p className="font-medium">{source.type.toUpperCase()}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Records</p>
                    <p className="font-medium">{formatNumber(source.record_count)}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Last Sync</p>
                    <p className="font-medium">{formatDate(source.last_sync)}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Errors</p>
                    <p className="font-medium text-red-600">{source.error_count}</p>
                  </div>
                </div>

                {source.sync_status === 'pending' && (
                  <div className="mt-3">
                    <Progress value={45} className="h-2" />
                    <p className="text-xs text-gray-500 mt-1">Syncing in progress...</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Realie API Status */}
      <Card className="border-2 border-blue-200 bg-gradient-to-r from-blue-50 to-indigo-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-blue-900">
            <Database className="h-5 w-5" />
            Realie API Integration Status
          </CardTitle>
          <CardDescription className="text-blue-700">
            Primary data source for immediate property coverage
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Current Status</h4>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">API Connection</span>
                  <Badge className="bg-green-100 text-green-800 border-green-200">
                    <CheckCircle className="h-3 w-3 mr-1" />
                    Connected
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Rate Limit</span>
                  <span className="text-sm font-medium">45/60 requests/min</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Data Freshness</span>
                  <span className="text-sm font-medium">2 hours ago</span>
                </div>
              </div>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Recent Activity</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Properties Added Today</span>
                  <span className="font-medium">127</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Properties Updated</span>
                  <span className="font-medium">89</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">API Calls Made</span>
                  <span className="font-medium">1,234</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Success Rate</span>
                  <span className="font-medium text-green-600">99.2%</span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* ATTOM Data Preparation */}
      <Card className="border-2 border-orange-200 bg-gradient-to-r from-orange-50 to-amber-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-orange-900">
            <Database className="h-5 w-5" />
            ATTOM Data Integration (Coming Soon)
          </CardTitle>
          <CardDescription className="text-orange-700">
            Historical data and deeper analytics for enriched insights
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Integration Progress</h4>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">API Setup</span>
                  <Badge className="bg-yellow-100 text-yellow-800 border-yellow-200">
                    In Progress
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Data Mapping</span>
                  <Badge className="bg-gray-100 text-gray-800 border-gray-200">
                    Pending
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Testing</span>
                  <Badge className="bg-gray-100 text-gray-800 border-gray-200">
                    Pending
                  </Badge>
                </div>
              </div>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Expected Benefits</h4>
              <ul className="space-y-2 text-sm text-gray-700">
                <li className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  Historical property data
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  Market trend analysis
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  Property tax information
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  Neighborhood demographics
                </li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Add New Source Modal */}
      {showAddSource && (
        <Card className="border-2 border-purple-200">
          <CardHeader>
            <CardTitle className="text-purple-900">Add New Data Source</CardTitle>
            <CardDescription>Configure a new property data source</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <Label htmlFor="source-name">Source Name</Label>
                <Input
                  id="source-name"
                  value={newSource.name}
                  onChange={(e) => setNewSource(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="e.g., MLS Database"
                />
              </div>
              <div>
                <Label htmlFor="source-type">Source Type</Label>
                <select
                  id="source-type"
                  value={newSource.type}
                  onChange={(e) => setNewSource(prev => ({ ...prev, type: e.target.value }))}
                  className="w-full p-2 border rounded-md"
                  aria-label="Select source type"
                >
                  <option value="api">API</option>
                  <option value="database">Database</option>
                  <option value="file">File Upload</option>
                  <option value="stream">Data Stream</option>
                </select>
              </div>
              <div>
                <Label htmlFor="base-url">Base URL</Label>
                <Input
                  id="base-url"
                  value={newSource.base_url}
                  onChange={(e) => setNewSource(prev => ({ ...prev, base_url: e.target.value }))}
                  placeholder="https://api.example.com/v1"
                />
              </div>
              <div>
                <Label htmlFor="api-key">API Key (Optional)</Label>
                <Input
                  id="api-key"
                  type="password"
                  value={newSource.api_key}
                  onChange={(e) => setNewSource(prev => ({ ...prev, api_key: e.target.value }))}
                  placeholder="Enter API key if required"
                />
              </div>
              <div className="flex gap-2">
                <Button onClick={handleAddSource} className="flex-1">
                  Add Source
                </Button>
                <Button 
                  variant="outline" 
                  onClick={() => setShowAddSource(false)}
                  className="flex-1"
                >
                  Cancel
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default DataIntegrationDashboard;
