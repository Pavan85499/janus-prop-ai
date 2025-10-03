import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { 
  Calculator, 
  TrendingUp, 
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
  Plus
} from "lucide-react";
import { AppLayout } from '@/components/layout/AppLayout';

interface UnderwritingAnalysis {
  id: number;
  property_id: number;
  property_address: string;
  status: string;
  created_at: string;
  purchase_price: number;
  estimated_value: number;
  monthly_rent: number;
  monthly_expenses: number;
  monthly_cash_flow: number;
  cap_rate: number;
  cash_on_cash_return: number;
  irr: number;
  noi: number;
  dscr: number;
  ltv: number;
  ai_analysis: string;
  risk_score: number;
  recommendation: string;
}

interface RentComp {
  id: number;
  property_address: string;
  rent: number;
  sqft: number;
  rent_per_sqft: number;
  bedrooms: number;
  bathrooms: number;
  distance_miles: number;
  comp_score: number;
}

interface RenovationScenario {
  id: number;
  scenario_name: string;
  renovation_cost: number;
  expected_rent_increase: number;
  expected_value_increase: number;
  roi: number;
  payback_period: number;
  risk_level: string;
}

const Underwriting: React.FC = () => {
  const [analyses, setAnalyses] = useState<UnderwritingAnalysis[]>([]);
  const [rentComps, setRentComps] = useState<RentComp[]>([]);
  const [renovationScenarios, setRenovationScenarios] = useState<RenovationScenario[]>([]);
  const [selectedAnalysis, setSelectedAnalysis] = useState<UnderwritingAnalysis | null>(null);
  const [isRunning, setIsRunning] = useState(false);

  // Mock data
  useEffect(() => {
    setAnalyses([
      {
        id: 1,
        property_id: 1,
        property_address: "123 Main St, Anytown, ST 12345",
        status: "completed",
        created_at: "2024-01-15T10:30:00Z",
        purchase_price: 450000,
        estimated_value: 475000,
        monthly_rent: 3200,
        monthly_expenses: 1800,
        monthly_cash_flow: 1400,
        cap_rate: 8.1,
        cash_on_cash_return: 12.5,
        irr: 15.2,
        noi: 16800,
        dscr: 1.8,
        ltv: 80,
        ai_analysis: "Strong investment opportunity with excellent cash flow and appreciation potential.",
        risk_score: 25,
        recommendation: "Proceed with purchase"
      },
      {
        id: 2,
        property_id: 2,
        property_address: "456 Oak Ave, Anytown, ST 12345",
        status: "in_progress",
        created_at: "2024-01-15T11:45:00Z",
        purchase_price: 320000,
        estimated_value: 0,
        monthly_rent: 0,
        monthly_expenses: 0,
        monthly_cash_flow: 0,
        cap_rate: 0,
        cash_on_cash_return: 0,
        irr: 0,
        noi: 0,
        dscr: 0,
        ltv: 0,
        ai_analysis: "",
        risk_score: 0,
        recommendation: ""
      }
    ]);

    setRentComps([
      {
        id: 1,
        property_address: "789 Pine St, Anytown, ST 12345",
        rent: 3100,
        sqft: 1200,
        rent_per_sqft: 2.58,
        bedrooms: 3,
        bathrooms: 2,
        distance_miles: 0.3,
        comp_score: 95
      },
      {
        id: 2,
        property_address: "321 Elm St, Anytown, ST 12345",
        rent: 3300,
        sqft: 1250,
        rent_per_sqft: 2.64,
        bedrooms: 3,
        bathrooms: 2.5,
        distance_miles: 0.5,
        comp_score: 88
      },
      {
        id: 3,
        property_address: "654 Maple Dr, Anytown, ST 12345",
        rent: 2950,
        sqft: 1150,
        rent_per_sqft: 2.57,
        bedrooms: 3,
        bathrooms: 2,
        distance_miles: 0.7,
        comp_score: 92
      }
    ]);

    setRenovationScenarios([
      {
        id: 1,
        scenario_name: "Kitchen & Bathroom Renovation",
        renovation_cost: 25000,
        expected_rent_increase: 300,
        expected_value_increase: 40000,
        roi: 172,
        payback_period: 6.9,
        risk_level: "low"
      },
      {
        id: 2,
        scenario_name: "Full Property Renovation",
        renovation_cost: 75000,
        expected_rent_increase: 800,
        expected_value_increase: 120000,
        roi: 160,
        payback_period: 7.5,
        risk_level: "medium"
      },
      {
        id: 3,
        scenario_name: "Cosmetic Updates Only",
        renovation_cost: 10000,
        expected_rent_increase: 150,
        expected_value_increase: 15000,
        roi: 150,
        payback_period: 6.7,
        risk_level: "low"
      }
    ]);
  }, []);

  const handleRunAnalysis = async (propertyId: number) => {
    setIsRunning(true);
    
    // Simulate analysis running
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Update analysis status
    setAnalyses(prev => prev.map(analysis => 
      analysis.property_id === propertyId 
        ? { ...analysis, status: "completed" }
        : analysis
    ));
    
    setIsRunning(false);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'in_progress':
        return 'bg-yellow-100 text-yellow-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getRiskLevelColor = (riskScore: number) => {
    if (riskScore <= 30) return 'text-green-600';
    if (riskScore <= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getRecommendationColor = (recommendation: string) => {
    switch (recommendation.toLowerCase()) {
      case 'proceed with purchase':
        return 'text-green-600';
      case 'proceed with caution':
        return 'text-yellow-600';
      case 'do not proceed':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <AppLayout>
      <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Automated Underwriting</h1>
          <p className="text-muted-foreground">
            AI-powered property analysis and investment evaluation
          </p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          New Analysis
        </Button>
      </div>

      <Tabs defaultValue="analyses" className="space-y-4">
        <TabsList>
          <TabsTrigger value="analyses">Analyses</TabsTrigger>
          <TabsTrigger value="rent-comps">Rent Comps</TabsTrigger>
          <TabsTrigger value="renovation">Renovation Scenarios</TabsTrigger>
          <TabsTrigger value="reports">Reports</TabsTrigger>
        </TabsList>

        <TabsContent value="analyses" className="space-y-4">
          <div className="grid gap-4">
            {analyses.map((analysis) => (
              <Card key={analysis.id}>
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-4 mb-4">
                        <h3 className="text-lg font-medium">{analysis.property_address}</h3>
                        <Badge className={getStatusColor(analysis.status)}>
                          {analysis.status === 'completed' && <CheckCircle className="h-3 w-3 mr-1" />}
                          {analysis.status === 'in_progress' && <RefreshCw className="h-3 w-3 mr-1 animate-spin" />}
                          {analysis.status === 'failed' && <AlertTriangle className="h-3 w-3 mr-1" />}
                          {analysis.status.replace('_', ' ')}
                        </Badge>
                        <span className="text-sm text-gray-500">
                          {new Date(analysis.created_at).toLocaleDateString()}
                        </span>
                      </div>

                      {analysis.status === 'completed' ? (
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                          <div className="text-center">
                            <p className="text-2xl font-bold text-green-600">
                              ${analysis.monthly_cash_flow.toLocaleString()}
                            </p>
                            <p className="text-sm text-gray-500">Monthly Cash Flow</p>
                          </div>
                          <div className="text-center">
                            <p className="text-2xl font-bold text-blue-600">
                              {analysis.cap_rate}%
                            </p>
                            <p className="text-sm text-gray-500">Cap Rate</p>
                          </div>
                          <div className="text-center">
                            <p className="text-2xl font-bold text-purple-600">
                              {analysis.cash_on_cash_return}%
                            </p>
                            <p className="text-sm text-gray-500">Cash on Cash Return</p>
                          </div>
                          <div className="text-center">
                            <p className={`text-2xl font-bold ${getRiskLevelColor(analysis.risk_score)}`}>
                              {analysis.risk_score}
                            </p>
                            <p className="text-sm text-gray-500">Risk Score</p>
                          </div>
                        </div>
                      ) : (
                        <div className="flex items-center space-x-4 mb-4">
                          <Progress value={analysis.status === 'in_progress' ? 65 : 0} className="flex-1" />
                          <span className="text-sm text-gray-500">
                            {analysis.status === 'in_progress' ? 'Analyzing...' : 'Ready to start'}
                          </span>
                        </div>
                      )}

                      {analysis.status === 'completed' && (
                        <div className="space-y-3">
                          <div className="p-4 bg-blue-50 rounded-lg">
                            <p className="text-sm text-blue-800">
                              <strong>AI Analysis:</strong> {analysis.ai_analysis}
                            </p>
                          </div>
                          <div className="flex items-center justify-between">
                            <p className={`font-medium ${getRecommendationColor(analysis.recommendation)}`}>
                              <strong>Recommendation:</strong> {analysis.recommendation}
                            </p>
                            <div className="flex space-x-2">
                              <Button variant="outline" size="sm">
                                <Eye className="h-4 w-4 mr-1" />
                                View Details
                              </Button>
                              <Button variant="outline" size="sm">
                                <Download className="h-4 w-4 mr-1" />
                                Export
                              </Button>
                            </div>
                          </div>
                        </div>
                      )}

                      {analysis.status === 'pending' && (
                        <div className="flex justify-end">
                          <Button 
                            onClick={() => handleRunAnalysis(analysis.property_id)}
                            disabled={isRunning}
                          >
                            {isRunning ? (
                              <>
                                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                                Running Analysis...
                              </>
                            ) : (
                              <>
                                <Play className="h-4 w-4 mr-2" />
                                Run Analysis
                              </>
                            )}
                          </Button>
                        </div>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="rent-comps" className="space-y-4">
          <div className="grid gap-4">
            {rentComps.map((comp) => (
              <Card key={comp.id}>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h3 className="text-lg font-medium">{comp.property_address}</h3>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                        <div>
                          <p className="text-2xl font-bold text-green-600">
                            ${comp.rent.toLocaleString()}
                          </p>
                          <p className="text-sm text-gray-500">Monthly Rent</p>
                        </div>
                        <div>
                          <p className="text-2xl font-bold text-blue-600">
                            ${comp.rent_per_sqft}
                          </p>
                          <p className="text-sm text-gray-500">Rent per Sq Ft</p>
                        </div>
                        <div>
                          <p className="text-2xl font-bold text-purple-600">
                            {comp.sqft.toLocaleString()}
                          </p>
                          <p className="text-sm text-gray-500">Square Feet</p>
                        </div>
                        <div>
                          <p className="text-2xl font-bold text-orange-600">
                            {comp.comp_score}%
                          </p>
                          <p className="text-sm text-gray-500">Comp Score</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4 mt-4">
                        <Badge variant="outline">
                          {comp.bedrooms} bed / {comp.bathrooms} bath
                        </Badge>
                        <Badge variant="outline">
                          {comp.distance_miles} miles away
                        </Badge>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="renovation" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {renovationScenarios.map((scenario) => (
              <Card key={scenario.id}>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    {scenario.scenario_name}
                    <Badge 
                      variant={scenario.risk_level === 'low' ? 'default' : scenario.risk_level === 'medium' ? 'secondary' : 'destructive'}
                    >
                      {scenario.risk_level} risk
                    </Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-2xl font-bold text-green-600">
                          {scenario.roi}%
                        </p>
                        <p className="text-sm text-gray-500">ROI</p>
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-blue-600">
                          {scenario.payback_period} years
                        </p>
                        <p className="text-sm text-gray-500">Payback Period</p>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-500">Renovation Cost:</span>
                        <span className="font-medium">${scenario.renovation_cost.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-500">Rent Increase:</span>
                        <span className="font-medium">+${scenario.expected_rent_increase}/month</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-500">Value Increase:</span>
                        <span className="font-medium">+${scenario.expected_value_increase.toLocaleString()}</span>
                      </div>
                    </div>
                    <Button className="w-full">
                      <Calculator className="h-4 w-4 mr-2" />
                      Analyze Scenario
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="reports" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Total Analyses</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{analyses.length}</div>
                <p className="text-xs text-muted-foreground">+3 this month</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Completed</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {analyses.filter(a => a.status === 'completed').length}
                </div>
                <p className="text-xs text-muted-foreground">95% success rate</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Avg Cap Rate</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {analyses.filter(a => a.status === 'completed').length > 0 
                    ? (analyses.filter(a => a.status === 'completed').reduce((sum, a) => sum + a.cap_rate, 0) / analyses.filter(a => a.status === 'completed').length).toFixed(1)
                    : 0}%
                </div>
                <p className="text-xs text-muted-foreground">Market average: 7.2%</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Avg Cash Flow</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  ${analyses.filter(a => a.status === 'completed').length > 0 
                    ? Math.round(analyses.filter(a => a.status === 'completed').reduce((sum, a) => sum + a.monthly_cash_flow, 0) / analyses.filter(a => a.status === 'completed').length)
                    : 0}
                </div>
                <p className="text-xs text-muted-foreground">Monthly average</p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
      </div>
    </AppLayout>
  );
};

export default Underwriting;
