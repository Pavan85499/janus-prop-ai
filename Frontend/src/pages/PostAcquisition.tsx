import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Home, 
  BarChart3, 
  FileText,
  Play,
  Pause,
  CheckCircle,
  AlertTriangle,
  RefreshCw,
  Download,
  Eye,
  Plus,
  Building,
  Wrench,
  Users,
  CreditCard,
  Target,
  Calendar,
  PieChart
} from "lucide-react";
import { AppLayout } from '@/components/layout/AppLayout';

interface PostAcquisitionAsset {
  id: number;
  property_id: number;
  property_address: string;
  asset_name: string;
  status: string;
  acquisition_date: string;
  acquisition_price: number;
  current_value: number;
  total_investment: number;
  monthly_cash_flow: number;
  annual_cash_flow: number;
  cap_rate: number;
  cash_on_cash_return: number;
  performance_score: number;
  risk_score: number;
  opportunity_score: number;
  created_at: string;
}

interface RenovationProject {
  id: number;
  asset_id: number;
  project_name: string;
  description: string;
  status: string;
  estimated_cost: number;
  actual_cost: number;
  budget_variance: number;
  estimated_duration_days: number;
  actual_duration_days: number;
  start_date?: string;
  completion_date?: string;
  expected_roi: number;
  actual_roi: number;
  created_at: string;
}

interface RefinancingOpportunity {
  id: number;
  asset_id: number;
  opportunity_name: string;
  status: string;
  current_loan_balance: number;
  current_interest_rate: number;
  new_interest_rate: number;
  monthly_savings: number;
  annual_savings: number;
  break_even_months: number;
  opportunity_score: number;
  created_at: string;
}

interface AssetMonitoring {
  id: number;
  asset_id: number;
  monitoring_date: string;
  property_condition_score: number;
  market_performance_score: number;
  financial_performance_score: number;
  overall_score: number;
  occupancy_rate: number;
  market_rent_trend: string;
  alerts: string[];
  issues_identified: string[];
  created_at: string;
}

const PostAcquisition: React.FC = () => {
  const [assets, setAssets] = useState<PostAcquisitionAsset[]>([]);
  const [renovationProjects, setRenovationProjects] = useState<RenovationProject[]>([]);
  const [refinancingOpportunities, setRefinancingOpportunities] = useState<RefinancingOpportunity[]>([]);
  const [assetMonitoring, setAssetMonitoring] = useState<AssetMonitoring[]>([]);
  const [selectedAsset, setSelectedAsset] = useState<PostAcquisitionAsset | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');

  // Mock data
  useEffect(() => {
    setAssets([
      {
        id: 1,
        property_id: 1,
        property_address: "123 Main St, Anytown, ST 12345",
        asset_name: "Main Street Rental",
        status: "active",
        acquisition_date: "2024-01-15T00:00:00Z",
        acquisition_price: 450000,
        current_value: 475000,
        total_investment: 525000,
        monthly_cash_flow: 1400,
        annual_cash_flow: 16800,
        cap_rate: 8.1,
        cash_on_cash_return: 12.5,
        performance_score: 85,
        risk_score: 25,
        opportunity_score: 75,
        created_at: "2024-01-15T10:30:00Z"
      },
      {
        id: 2,
        property_id: 2,
        property_address: "456 Oak Ave, Anytown, ST 12345",
        asset_name: "Oak Avenue Flip",
        status: "under_renovation",
        acquisition_date: "2024-01-10T00:00:00Z",
        acquisition_price: 320000,
        current_value: 350000,
        total_investment: 380000,
        monthly_cash_flow: 0,
        annual_cash_flow: 0,
        cap_rate: 0,
        cash_on_cash_return: 0,
        performance_score: 0,
        risk_score: 45,
        opportunity_score: 90,
        created_at: "2024-01-10T14:20:00Z"
      },
      {
        id: 3,
        property_id: 3,
        property_address: "789 Pine St, Anytown, ST 12345",
        asset_name: "Pine Street Investment",
        status: "leased",
        acquisition_date: "2024-01-05T00:00:00Z",
        acquisition_price: 280000,
        current_value: 295000,
        total_investment: 300000,
        monthly_cash_flow: 1200,
        annual_cash_flow: 14400,
        cap_rate: 7.8,
        cash_on_cash_return: 11.2,
        performance_score: 78,
        risk_score: 30,
        opportunity_score: 65,
        created_at: "2024-01-05T09:15:00Z"
      }
    ]);

    setRenovationProjects([
      {
        id: 1,
        asset_id: 1,
        project_name: "Kitchen & Bathroom Renovation",
        description: "Complete renovation of kitchen and master bathroom",
        status: "completed",
        estimated_cost: 25000,
        actual_cost: 27500,
        budget_variance: 2500,
        estimated_duration_days: 30,
        actual_duration_days: 35,
        start_date: "2024-01-20T00:00:00Z",
        completion_date: "2024-02-24T00:00:00Z",
        expected_roi: 172,
        actual_roi: 165,
        created_at: "2024-01-15T10:30:00Z"
      },
      {
        id: 2,
        asset_id: 2,
        project_name: "Full Property Renovation",
        description: "Complete renovation of entire property",
        status: "in_progress",
        estimated_cost: 75000,
        actual_cost: 45000,
        budget_variance: -30000,
        estimated_duration_days: 60,
        actual_duration_days: 0,
        start_date: "2024-01-25T00:00:00Z",
        expected_roi: 160,
        actual_roi: 0,
        created_at: "2024-01-20T14:20:00Z"
      }
    ]);

    setRefinancingOpportunities([
      {
        id: 1,
        asset_id: 1,
        opportunity_name: "Rate Reduction Refinance",
        status: "eligible",
        current_loan_balance: 360000,
        current_interest_rate: 6.5,
        new_interest_rate: 5.8,
        monthly_savings: 210,
        annual_savings: 2520,
        break_even_months: 18,
        opportunity_score: 85,
        created_at: "2024-01-15T10:30:00Z"
      },
      {
        id: 2,
        asset_id: 3,
        opportunity_name: "Cash-Out Refinance",
        status: "eligible",
        current_loan_balance: 224000,
        current_interest_rate: 6.2,
        new_interest_rate: 5.9,
        monthly_savings: 45,
        annual_savings: 540,
        break_even_months: 24,
        opportunity_score: 65,
        created_at: "2024-01-10T09:15:00Z"
      }
    ]);

    setAssetMonitoring([
      {
        id: 1,
        asset_id: 1,
        monitoring_date: "2024-01-15T00:00:00Z",
        property_condition_score: 90,
        market_performance_score: 85,
        financial_performance_score: 88,
        overall_score: 88,
        occupancy_rate: 100,
        market_rent_trend: "rising",
        alerts: [],
        issues_identified: [],
        created_at: "2024-01-15T10:30:00Z"
      },
      {
        id: 2,
        asset_id: 2,
        monitoring_date: "2024-01-15T00:00:00Z",
        property_condition_score: 60,
        market_performance_score: 80,
        financial_performance_score: 0,
        overall_score: 47,
        occupancy_rate: 0,
        market_rent_trend: "stable",
        alerts: ["Renovation in progress", "No rental income"],
        issues_identified: ["Budget overrun", "Timeline delay"],
        created_at: "2024-01-15T10:30:00Z"
      }
    ]);
  }, []);

  const filteredAssets = assets.filter(asset => {
    const matchesSearch = asset.property_address.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         asset.asset_name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === 'all' || asset.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'under_renovation':
        return 'bg-yellow-100 text-yellow-800';
      case 'leased':
        return 'bg-blue-100 text-blue-800';
      case 'vacant':
        return 'bg-gray-100 text-gray-800';
      case 'for_sale':
        return 'bg-purple-100 text-purple-800';
      case 'sold':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'rising':
        return <TrendingUp className="h-4 w-4 text-green-500" />;
      case 'falling':
        return <TrendingDown className="h-4 w-4 text-red-500" />;
      default:
        return <BarChart3 className="h-4 w-4 text-gray-500" />;
    }
  };

  return (
    <AppLayout>
      <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Post-Acquisition Intelligence</h1>
          <p className="text-muted-foreground">
            Monitor and optimize your real estate investments with AI-powered insights
          </p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Add Asset
        </Button>
      </div>

      <Tabs defaultValue="assets" className="space-y-4">
        <TabsList>
          <TabsTrigger value="assets">Portfolio Assets</TabsTrigger>
          <TabsTrigger value="renovations">Renovation Projects</TabsTrigger>
          <TabsTrigger value="refinancing">Refinancing Opportunities</TabsTrigger>
          <TabsTrigger value="monitoring">Asset Monitoring</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="assets" className="space-y-4">
          {/* Search and Filters */}
          <Card>
            <CardContent className="pt-6">
              <div className="flex gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Input
                      placeholder="Search assets..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-md"
                >
                  <option value="all">All Status</option>
                  <option value="active">Active</option>
                  <option value="under_renovation">Under Renovation</option>
                  <option value="leased">Leased</option>
                  <option value="vacant">Vacant</option>
                  <option value="for_sale">For Sale</option>
                  <option value="sold">Sold</option>
                </select>
              </div>
            </CardContent>
          </Card>

          {/* Assets List */}
          <div className="grid gap-4">
            {filteredAssets.map((asset) => (
              <Card key={asset.id}>
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-4 mb-4">
                        <h3 className="text-lg font-medium">{asset.asset_name}</h3>
                        <Badge className={getStatusColor(asset.status)}>
                          {asset.status.replace('_', ' ')}
                        </Badge>
                        <span className="text-sm text-gray-500">
                          Acquired: {new Date(asset.acquisition_date).toLocaleDateString()}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mb-4">{asset.property_address}</p>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                        <div className="text-center">
                          <p className="text-2xl font-bold text-green-600">
                            ${asset.monthly_cash_flow.toLocaleString()}
                          </p>
                          <p className="text-sm text-gray-500">Monthly Cash Flow</p>
                        </div>
                        <div className="text-center">
                          <p className="text-2xl font-bold text-blue-600">
                            {asset.cap_rate}%
                          </p>
                          <p className="text-sm text-gray-500">Cap Rate</p>
                        </div>
                        <div className="text-center">
                          <p className="text-2xl font-bold text-purple-600">
                            {asset.cash_on_cash_return}%
                          </p>
                          <p className="text-sm text-gray-500">Cash on Cash Return</p>
                        </div>
                        <div className="text-center">
                          <p className={`text-2xl font-bold ${getScoreColor(asset.performance_score)}`}>
                            {asset.performance_score}
                          </p>
                          <p className="text-sm text-gray-500">Performance Score</p>
                        </div>
                      </div>

                      <div className="grid grid-cols-3 gap-4 mb-4">
                        <div className="text-center">
                          <p className="text-lg font-bold text-green-600">
                            ${asset.current_value.toLocaleString()}
                          </p>
                          <p className="text-sm text-gray-500">Current Value</p>
                        </div>
                        <div className="text-center">
                          <p className="text-lg font-bold text-orange-600">
                            {asset.risk_score}
                          </p>
                          <p className="text-sm text-gray-500">Risk Score</p>
                        </div>
                        <div className="text-center">
                          <p className="text-lg font-bold text-blue-600">
                            {asset.opportunity_score}
                          </p>
                          <p className="text-sm text-gray-500">Opportunity Score</p>
                        </div>
                      </div>

                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <Badge variant="outline">
                            <DollarSign className="h-3 w-3 mr-1" />
                            Investment: ${asset.total_investment.toLocaleString()}
                          </Badge>
                          <Badge variant="outline">
                            <Home className="h-3 w-3 mr-1" />
                            Appreciation: ${(asset.current_value - asset.acquisition_price).toLocaleString()}
                          </Badge>
                        </div>
                        <div className="flex space-x-2">
                          <Button variant="outline" size="sm">
                            <Eye className="h-4 w-4 mr-1" />
                            View Details
                          </Button>
                          <Button variant="outline" size="sm">
                            <BarChart3 className="h-4 w-4 mr-1" />
                            Analytics
                          </Button>
                          <Button variant="outline" size="sm">
                            <Download className="h-4 w-4 mr-1" />
                            Export
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="renovations" className="space-y-4">
          <div className="grid gap-4">
            {renovationProjects.map((project) => (
              <Card key={project.id}>
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-4 mb-4">
                        <h3 className="text-lg font-medium">{project.project_name}</h3>
                        <Badge className={getStatusColor(project.status)}>
                          {project.status.replace('_', ' ')}
                        </Badge>
                        <span className="text-sm text-gray-500">
                          {new Date(project.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mb-4">{project.description}</p>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                        <div className="text-center">
                          <p className="text-2xl font-bold text-green-600">
                            ${project.estimated_cost.toLocaleString()}
                          </p>
                          <p className="text-sm text-gray-500">Estimated Cost</p>
                        </div>
                        <div className="text-center">
                          <p className="text-2xl font-bold text-blue-600">
                            ${project.actual_cost.toLocaleString()}
                          </p>
                          <p className="text-sm text-gray-500">Actual Cost</p>
                        </div>
                        <div className="text-center">
                          <p className={`text-2xl font-bold ${project.budget_variance >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                            {project.budget_variance >= 0 ? '+' : ''}${project.budget_variance.toLocaleString()}
                          </p>
                          <p className="text-sm text-gray-500">Budget Variance</p>
                        </div>
                        <div className="text-center">
                          <p className="text-2xl font-bold text-purple-600">
                            {project.expected_roi}%
                          </p>
                          <p className="text-sm text-gray-500">Expected ROI</p>
                        </div>
                      </div>

                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <Badge variant="outline">
                            <Calendar className="h-3 w-3 mr-1" />
                            Duration: {project.actual_duration_days || project.estimated_duration_days} days
                          </Badge>
                          {project.start_date && (
                            <Badge variant="outline">
                              <Calendar className="h-3 w-3 mr-1" />
                              Started: {new Date(project.start_date).toLocaleDateString()}
                            </Badge>
                          )}
                          {project.completion_date && (
                            <Badge variant="outline">
                              <CheckCircle className="h-3 w-3 mr-1" />
                              Completed: {new Date(project.completion_date).toLocaleDateString()}
                            </Badge>
                          )}
                        </div>
                        <div className="flex space-x-2">
                          <Button variant="outline" size="sm">
                            <Eye className="h-4 w-4 mr-1" />
                            View Details
                          </Button>
                          <Button variant="outline" size="sm">
                            <Wrench className="h-4 w-4 mr-1" />
                            Update Progress
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="refinancing" className="space-y-4">
          <div className="grid gap-4">
            {refinancingOpportunities.map((opportunity) => (
              <Card key={opportunity.id}>
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-4 mb-4">
                        <h3 className="text-lg font-medium">{opportunity.opportunity_name}</h3>
                        <Badge className={getStatusColor(opportunity.status)}>
                          {opportunity.status}
                        </Badge>
                        <span className="text-sm text-gray-500">
                          {new Date(opportunity.created_at).toLocaleDateString()}
                        </span>
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                        <div className="text-center">
                          <p className="text-2xl font-bold text-green-600">
                            ${opportunity.monthly_savings.toLocaleString()}
                          </p>
                          <p className="text-sm text-gray-500">Monthly Savings</p>
                        </div>
                        <div className="text-center">
                          <p className="text-2xl font-bold text-blue-600">
                            ${opportunity.annual_savings.toLocaleString()}
                          </p>
                          <p className="text-sm text-gray-500">Annual Savings</p>
                        </div>
                        <div className="text-center">
                          <p className="text-2xl font-bold text-purple-600">
                            {opportunity.break_even_months}
                          </p>
                          <p className="text-sm text-gray-500">Break-even (months)</p>
                        </div>
                        <div className="text-center">
                          <p className={`text-2xl font-bold ${getScoreColor(opportunity.opportunity_score)}`}>
                            {opportunity.opportunity_score}
                          </p>
                          <p className="text-sm text-gray-500">Opportunity Score</p>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4 mb-4">
                        <div className="text-center">
                          <p className="text-lg font-bold text-orange-600">
                            {opportunity.current_interest_rate}%
                          </p>
                          <p className="text-sm text-gray-500">Current Rate</p>
                        </div>
                        <div className="text-center">
                          <p className="text-lg font-bold text-green-600">
                            {opportunity.new_interest_rate}%
                          </p>
                          <p className="text-sm text-gray-500">New Rate</p>
                        </div>
                      </div>

                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <Badge variant="outline">
                            <DollarSign className="h-3 w-3 mr-1" />
                            Loan Balance: ${opportunity.current_loan_balance.toLocaleString()}
                          </Badge>
                          <Badge variant="outline">
                            <Target className="h-3 w-3 mr-1" />
                            Rate Reduction: {(opportunity.current_interest_rate - opportunity.new_interest_rate).toFixed(1)}%
                          </Badge>
                        </div>
                        <div className="flex space-x-2">
                          <Button variant="outline" size="sm">
                            <Eye className="h-4 w-4 mr-1" />
                            View Details
                          </Button>
                          <Button variant="outline" size="sm">
                            <CreditCard className="h-4 w-4 mr-1" />
                            Apply
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="monitoring" className="space-y-4">
          <div className="grid gap-4">
            {assetMonitoring.map((monitoring) => (
              <Card key={monitoring.id}>
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-4 mb-4">
                        <h3 className="text-lg font-medium">Asset Monitoring Report</h3>
                        <Badge variant="outline">
                          {new Date(monitoring.monitoring_date).toLocaleDateString()}
                        </Badge>
                        <div className="flex items-center">
                          {getTrendIcon(monitoring.market_rent_trend)}
                          <span className="ml-1 text-sm text-gray-500 capitalize">
                            {monitoring.market_rent_trend}
                          </span>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                        <div className="text-center">
                          <p className={`text-2xl font-bold ${getScoreColor(monitoring.overall_score)}`}>
                            {monitoring.overall_score}
                          </p>
                          <p className="text-sm text-gray-500">Overall Score</p>
                        </div>
                        <div className="text-center">
                          <p className={`text-2xl font-bold ${getScoreColor(monitoring.property_condition_score)}`}>
                            {monitoring.property_condition_score}
                          </p>
                          <p className="text-sm text-gray-500">Property Condition</p>
                        </div>
                        <div className="text-center">
                          <p className={`text-2xl font-bold ${getScoreColor(monitoring.market_performance_score)}`}>
                            {monitoring.market_performance_score}
                          </p>
                          <p className="text-sm text-gray-500">Market Performance</p>
                        </div>
                        <div className="text-center">
                          <p className={`text-2xl font-bold ${getScoreColor(monitoring.financial_performance_score)}`}>
                            {monitoring.financial_performance_score}
                          </p>
                          <p className="text-sm text-gray-500">Financial Performance</p>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4 mb-4">
                        <div className="text-center">
                          <p className="text-lg font-bold text-blue-600">
                            {monitoring.occupancy_rate}%
                          </p>
                          <p className="text-sm text-gray-500">Occupancy Rate</p>
                        </div>
                        <div className="text-center">
                          <p className="text-lg font-bold text-green-600">
                            {monitoring.market_rent_trend}
                          </p>
                          <p className="text-sm text-gray-500">Rent Trend</p>
                        </div>
                      </div>

                      {monitoring.alerts.length > 0 && (
                        <div className="p-4 bg-yellow-50 rounded-lg mb-4">
                          <h4 className="font-medium text-yellow-800 mb-2">Alerts</h4>
                          <ul className="list-disc list-inside space-y-1">
                            {monitoring.alerts.map((alert, index) => (
                              <li key={index} className="text-sm text-yellow-700">{alert}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {monitoring.issues_identified.length > 0 && (
                        <div className="p-4 bg-red-50 rounded-lg mb-4">
                          <h4 className="font-medium text-red-800 mb-2">Issues Identified</h4>
                          <ul className="list-disc list-inside space-y-1">
                            {monitoring.issues_identified.map((issue, index) => (
                              <li key={index} className="text-sm text-red-700">{issue}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      <div className="flex justify-end space-x-2">
                        <Button variant="outline" size="sm">
                          <Eye className="h-4 w-4 mr-1" />
                          View Full Report
                        </Button>
                        <Button variant="outline" size="sm">
                          <Download className="h-4 w-4 mr-1" />
                          Export
                        </Button>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Total Assets</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{assets.length}</div>
                <p className="text-xs text-muted-foreground">+2 this month</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Active Assets</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {assets.filter(a => a.status === 'active').length}
                </div>
                <p className="text-xs text-muted-foreground">Generating income</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Avg Performance Score</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {assets.filter(a => a.performance_score > 0).length > 0 
                    ? Math.round(assets.filter(a => a.performance_score > 0).reduce((sum, a) => sum + a.performance_score, 0) / assets.filter(a => a.performance_score > 0).length)
                    : 0}
                </div>
                <p className="text-xs text-muted-foreground">Portfolio average</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Total Cash Flow</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  ${assets.reduce((sum, a) => sum + a.monthly_cash_flow, 0).toLocaleString()}
                </div>
                <p className="text-xs text-muted-foreground">Monthly total</p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
      </div>
    </AppLayout>
  );
};

export default PostAcquisition;
