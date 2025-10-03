import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Home, 
  Calculator, 
  FileText,
  Shield,
  Users,
  Clock,
  CheckCircle,
  AlertTriangle,
  Activity,
  BarChart3,
  PieChart,
  LineChart
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface PropertyIntelligenceData {
  propertyId: string;
  address: string;
  analysisStatus: 'pending' | 'in_progress' | 'completed' | 'failed';
  progress: number;
  underwritingResults?: {
    monthlyCashFlow: number;
    cashOnCashReturn: number;
    capRate: number;
    riskRating: 'A' | 'B' | 'C' | 'D';
  };
  legalCompliance?: {
    overallStatus: 'compliant' | 'requires_attention' | 'non_compliant';
    issuesCount: number;
    riskLevel: 'low' | 'medium' | 'high' | 'critical';
  };
  investmentCommittee?: {
    decision: 'strong_buy' | 'buy' | 'hold' | 'pass' | 'avoid';
    confidence: number;
    unanimousDecision: boolean;
  };
  marketData?: {
    priceToValue: number;
    marketTrend: 'up' | 'down' | 'stable';
    comparableCount: number;
  };
  lastUpdated: string;
}

interface PropertyIntelligenceDashboardProps {
  propertyData: PropertyIntelligenceData;
  onRefresh?: () => void;
}

export function PropertyIntelligenceDashboard({ 
  propertyData, 
  onRefresh 
}: PropertyIntelligenceDashboardProps) {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [animationKey, setAnimationKey] = useState(0);

  useEffect(() => {
    // Trigger animation when data updates
    setAnimationKey(prev => prev + 1);
  }, [propertyData]);

  const handleRefresh = async () => {
    if (onRefresh) {
      setIsRefreshing(true);
      await onRefresh();
      setIsRefreshing(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-success';
      case 'in_progress': return 'text-warning';
      case 'failed': return 'text-destructive';
      default: return 'text-muted-foreground';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="w-4 h-4" />;
      case 'in_progress': return <Clock className="w-4 h-4 animate-spin" />;
      case 'failed': return <AlertTriangle className="w-4 h-4" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  const getRiskRatingColor = (rating: string) => {
    switch (rating) {
      case 'A': return 'bg-success text-success-foreground';
      case 'B': return 'bg-warning text-warning-foreground';
      case 'C': return 'bg-orange-500 text-white';
      case 'D': return 'bg-destructive text-destructive-foreground';
      default: return 'bg-muted text-muted-foreground';
    }
  };

  const getDecisionColor = (decision: string) => {
    switch (decision) {
      case 'strong_buy': return 'bg-green-600 text-white';
      case 'buy': return 'bg-success text-success-foreground';
      case 'hold': return 'bg-warning text-warning-foreground';
      case 'pass': return 'bg-orange-500 text-white';
      case 'avoid': return 'bg-destructive text-destructive-foreground';
      default: return 'bg-muted text-muted-foreground';
    }
  };

  const getComplianceColor = (status: string) => {
    switch (status) {
      case 'compliant': return 'text-success';
      case 'requires_attention': return 'text-warning';
      case 'non_compliant': return 'text-destructive';
      default: return 'text-muted-foreground';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-foreground">
            Property Intelligence Dashboard
          </h2>
          <p className="text-muted-foreground">{propertyData.address}</p>
        </div>
        <div className="flex items-center gap-2">
          <Badge 
            variant="outline" 
            className={getStatusColor(propertyData.analysisStatus)}
          >
            {getStatusIcon(propertyData.analysisStatus)}
            <span className="ml-1 capitalize">
              {propertyData.analysisStatus.replace('_', ' ')}
            </span>
          </Badge>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={handleRefresh}
            disabled={isRefreshing}
          >
            <Activity className={`w-4 h-4 mr-1 ${isRefreshing ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Progress Bar */}
      {propertyData.analysisStatus === 'in_progress' && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">Analysis Progress</span>
            <span className="text-sm text-muted-foreground">{propertyData.progress}%</span>
          </div>
          <Progress value={propertyData.progress} className="w-full" />
        </motion.div>
      )}

      {/* Main Dashboard Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Underwriting Results */}
        {propertyData.underwritingResults && (
          <motion.div
            key={`underwriting-${animationKey}`}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
          >
            <Card className="border-l-4 border-l-blue-500">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Calculator className="w-4 h-4 text-blue-500" />
                  Underwriting Analysis
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">Monthly Cash Flow</span>
                  <div className="flex items-center gap-1">
                    {propertyData.underwritingResults.monthlyCashFlow >= 0 ? (
                      <TrendingUp className="w-3 h-3 text-success" />
                    ) : (
                      <TrendingDown className="w-3 h-3 text-destructive" />
                    )}
                    <span className={`text-sm font-semibold ${
                      propertyData.underwritingResults.monthlyCashFlow >= 0 
                        ? 'text-success' 
                        : 'text-destructive'
                    }`}>
                      ${propertyData.underwritingResults.monthlyCashFlow.toLocaleString()}
                    </span>
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">Cash-on-Cash Return</span>
                  <span className="text-sm font-semibold">
                    {(propertyData.underwritingResults.cashOnCashReturn * 100).toFixed(1)}%
                  </span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">Cap Rate</span>
                  <span className="text-sm font-semibold">
                    {(propertyData.underwritingResults.capRate * 100).toFixed(1)}%
                  </span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">Risk Rating</span>
                  <Badge className={getRiskRatingColor(propertyData.underwritingResults.riskRating)}>
                    {propertyData.underwritingResults.riskRating}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Legal Compliance */}
        {propertyData.legalCompliance && (
          <motion.div
            key={`legal-${animationKey}`}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3, delay: 0.1 }}
          >
            <Card className="border-l-4 border-l-purple-500">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Shield className="w-4 h-4 text-purple-500" />
                  Legal Compliance
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">Overall Status</span>
                  <Badge 
                    variant="outline" 
                    className={getComplianceColor(propertyData.legalCompliance.overallStatus)}
                  >
                    {propertyData.legalCompliance.overallStatus.replace('_', ' ')}
                  </Badge>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">Issues Found</span>
                  <span className="text-sm font-semibold">
                    {propertyData.legalCompliance.issuesCount}
                  </span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">Risk Level</span>
                  <Badge 
                    variant={propertyData.legalCompliance.riskLevel === 'low' ? 'default' : 'destructive'}
                  >
                    {propertyData.legalCompliance.riskLevel}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Investment Committee */}
        {propertyData.investmentCommittee && (
          <motion.div
            key={`committee-${animationKey}`}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3, delay: 0.2 }}
          >
            <Card className="border-l-4 border-l-green-500">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Users className="w-4 h-4 text-green-500" />
                  Investment Committee
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">Decision</span>
                  <Badge className={getDecisionColor(propertyData.investmentCommittee.decision)}>
                    {propertyData.investmentCommittee.decision.replace('_', ' ')}
                  </Badge>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">Confidence</span>
                  <span className="text-sm font-semibold">
                    {(propertyData.investmentCommittee.confidence * 100).toFixed(0)}%
                  </span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">Consensus</span>
                  <div className="flex items-center gap-1">
                    {propertyData.investmentCommittee.unanimousDecision ? (
                      <CheckCircle className="w-3 h-3 text-success" />
                    ) : (
                      <AlertTriangle className="w-3 h-3 text-warning" />
                    )}
                    <span className="text-xs">
                      {propertyData.investmentCommittee.unanimousDecision ? 'Unanimous' : 'Majority'}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Market Data */}
        {propertyData.marketData && (
          <motion.div
            key={`market-${animationKey}`}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3, delay: 0.3 }}
          >
            <Card className="border-l-4 border-l-orange-500">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <BarChart3 className="w-4 h-4 text-orange-500" />
                  Market Analysis
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">Price to Value</span>
                  <span className="text-sm font-semibold">
                    {(propertyData.marketData.priceToValue * 100).toFixed(0)}%
                  </span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">Market Trend</span>
                  <div className="flex items-center gap-1">
                    {propertyData.marketData.marketTrend === 'up' && (
                      <TrendingUp className="w-3 h-3 text-success" />
                    )}
                    {propertyData.marketData.marketTrend === 'down' && (
                      <TrendingDown className="w-3 h-3 text-destructive" />
                    )}
                    {propertyData.marketData.marketTrend === 'stable' && (
                      <Activity className="w-3 h-3 text-muted-foreground" />
                    )}
                    <span className="text-xs capitalize">
                      {propertyData.marketData.marketTrend}
                    </span>
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">Comparables</span>
                  <span className="text-sm font-semibold">
                    {propertyData.marketData.comparableCount}
                  </span>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </div>

      {/* Detailed Analysis Section */}
      {propertyData.analysisStatus === 'completed' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5" />
                Comprehensive Analysis Summary
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Financial Summary */}
                <div className="space-y-3">
                  <h4 className="font-semibold text-sm flex items-center gap-2">
                    <DollarSign className="w-4 h-4" />
                    Financial Metrics
                  </h4>
                  {propertyData.underwritingResults && (
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Monthly Cash Flow:</span>
                        <span className={propertyData.underwritingResults.monthlyCashFlow >= 0 ? 'text-success' : 'text-destructive'}>
                          ${propertyData.underwritingResults.monthlyCashFlow.toLocaleString()}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Annual Return:</span>
                        <span>{(propertyData.underwritingResults.cashOnCashReturn * 100).toFixed(1)}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Cap Rate:</span>
                        <span>{(propertyData.underwritingResults.capRate * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                  )}
                </div>

                {/* Risk Assessment */}
                <div className="space-y-3">
                  <h4 className="font-semibold text-sm flex items-center gap-2">
                    <Shield className="w-4 h-4" />
                    Risk Assessment
                  </h4>
                  <div className="space-y-2 text-sm">
                    {propertyData.underwritingResults && (
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Financial Risk:</span>
                        <Badge className={getRiskRatingColor(propertyData.underwritingResults.riskRating)}>
                          {propertyData.underwritingResults.riskRating}
                        </Badge>
                      </div>
                    )}
                    {propertyData.legalCompliance && (
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Legal Risk:</span>
                        <Badge variant={propertyData.legalCompliance.riskLevel === 'low' ? 'default' : 'destructive'}>
                          {propertyData.legalCompliance.riskLevel}
                        </Badge>
                      </div>
                    )}
                  </div>
                </div>

                {/* Investment Recommendation */}
                <div className="space-y-3">
                  <h4 className="font-semibold text-sm flex items-center gap-2">
                    <Users className="w-4 h-4" />
                    Committee Decision
                  </h4>
                  {propertyData.investmentCommittee && (
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Recommendation:</span>
                        <Badge className={getDecisionColor(propertyData.investmentCommittee.decision)}>
                          {propertyData.investmentCommittee.decision.replace('_', ' ')}
                        </Badge>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Confidence:</span>
                        <span>{(propertyData.investmentCommittee.confidence * 100).toFixed(0)}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Consensus:</span>
                        <span>{propertyData.investmentCommittee.unanimousDecision ? 'Unanimous' : 'Majority'}</span>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              <Separator className="my-4" />
              
              <div className="text-xs text-muted-foreground">
                Last updated: {new Date(propertyData.lastUpdated).toLocaleString()}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </div>
  );
}

export default PropertyIntelligenceDashboard;