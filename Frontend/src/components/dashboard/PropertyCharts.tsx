import React, { useState, useEffect, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  LineChart, 
  Line, 
  AreaChart, 
  Area, 
  BarChart, 
  Bar, 
  PieChart, 
  Pie, 
  Cell,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  ScatterChart,
  Scatter
} from 'recharts';
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Home, 
  Activity,
  BarChart3,
  PieChart as PieChartIcon,
  Calendar,
  RefreshCw
} from 'lucide-react';
import { motion } from 'framer-motion';

interface PropertyMetrics {
  cashFlow: number;
  capRate: number;
  roiPercentage: number;
  occupancyRate: number;
  monthlyRent: number;
  operatingExpenses: number;
  timestamp: string;
}

interface MarketData {
  month: string;
  averagePrice: number;
  salesVolume: number;
  daysOnMarket: number;
  pricePerSqft: number;
}

interface PortfolioData {
  propertyType: string;
  count: number;
  totalValue: number;
  monthlyIncome: number;
  performance: 'excellent' | 'good' | 'average' | 'poor';
}

interface PropertyChartsProps {
  propertyMetrics: PropertyMetrics[];
  marketData: MarketData[];
  portfolioData: PortfolioData[];
  isLoading?: boolean;
  onRefresh?: () => void;
}

// Color schemes for charts
const COLORS = {
  primary: '#3B82F6',
  secondary: '#10B981',
  accent: '#F59E0B',
  warning: '#EF4444',
  muted: '#6B7280'
};

const PIE_COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

export function PropertyCharts({ 
  propertyMetrics, 
  marketData, 
  portfolioData, 
  isLoading = false,
  onRefresh 
}: PropertyChartsProps) {
  const [activeTab, setActiveTab] = useState('performance');
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = async () => {
    if (onRefresh) {
      setIsRefreshing(true);
      await onRefresh();
      setIsRefreshing(false);
    }
  };

  // Process data for different chart types
  const cashFlowData = useMemo(() => {
    return propertyMetrics.map(metric => ({
      month: new Date(metric.timestamp).toLocaleDateString('en-US', { month: 'short' }),
      cashFlow: metric.cashFlow,
      rent: metric.monthlyRent,
      expenses: metric.operatingExpenses,
      netIncome: metric.monthlyRent - metric.operatingExpenses
    }));
  }, [propertyMetrics]);

  const performanceData = useMemo(() => {
    return propertyMetrics.map(metric => ({
      month: new Date(metric.timestamp).toLocaleDateString('en-US', { month: 'short' }),
      capRate: metric.capRate * 100,
      roi: metric.roiPercentage,
      occupancy: metric.occupancyRate * 100
    }));
  }, [propertyMetrics]);

  const portfolioDistribution = useMemo(() => {
    return portfolioData.map(item => ({
      name: item.propertyType,
      value: item.totalValue,
      count: item.count,
      income: item.monthlyIncome
    }));
  }, [portfolioData]);

  const marketTrends = useMemo(() => {
    return marketData.map(data => ({
      month: data.month,
      price: data.averagePrice,
      volume: data.salesVolume,
      dom: data.daysOnMarket,
      pricePerSqft: data.pricePerSqft
    }));
  }, [marketData]);

  // Custom tooltip component
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className=\"bg-background border border-border rounded-lg shadow-lg p-3\">
          <p className=\"font-semibold\">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} style={{ color: entry.color }} className=\"text-sm\">
              {`${entry.dataKey}: ${typeof entry.value === 'number' ? 
                entry.value.toLocaleString() : entry.value}`}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  const LoadingOverlay = () => (
    <div className=\"absolute inset-0 bg-background/50 flex items-center justify-center z-10\">
      <div className=\"flex items-center gap-2 text-muted-foreground\">
        <RefreshCw className=\"w-4 h-4 animate-spin\" />
        <span>Loading chart data...</span>
      </div>
    </div>
  );

  return (
    <div className=\"space-y-6\">
      {/* Header */}
      <div className=\"flex items-center justify-between\">
        <div>
          <h2 className=\"text-2xl font-bold text-foreground\">
            Property Analytics Dashboard
          </h2>
          <p className=\"text-muted-foreground\">Real-time insights and performance metrics</p>
        </div>
        <Button 
          variant=\"outline\" 
          size=\"sm\" 
          onClick={handleRefresh}
          disabled={isRefreshing || isLoading}
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
          Refresh Data
        </Button>
      </div>

      {/* Summary Cards */}
      <div className=\"grid grid-cols-1 md:grid-cols-4 gap-4\">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <Card>
            <CardContent className=\"p-4\">
              <div className=\"flex items-center gap-3\">
                <div className=\"p-2 bg-blue-100 dark:bg-blue-900 rounded-lg\">
                  <DollarSign className=\"w-4 h-4 text-blue-600 dark:text-blue-400\" />
                </div>
                <div>
                  <p className=\"text-xs text-muted-foreground\">Avg Monthly Cash Flow</p>
                  <p className=\"text-lg font-semibold\">
                    ${propertyMetrics.length > 0 ? 
                      Math.round(propertyMetrics.reduce((sum, m) => sum + m.cashFlow, 0) / propertyMetrics.length).toLocaleString() : 
                      '0'
                    }
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.1 }}
        >
          <Card>
            <CardContent className=\"p-4\">
              <div className=\"flex items-center gap-3\">
                <div className=\"p-2 bg-green-100 dark:bg-green-900 rounded-lg\">
                  <TrendingUp className=\"w-4 h-4 text-green-600 dark:text-green-400\" />
                </div>
                <div>
                  <p className=\"text-xs text-muted-foreground\">Avg Cap Rate</p>
                  <p className=\"text-lg font-semibold\">
                    {propertyMetrics.length > 0 ? 
                      ((propertyMetrics.reduce((sum, m) => sum + m.capRate, 0) / propertyMetrics.length) * 100).toFixed(1) : 
                      '0.0'
                    }%
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.2 }}
        >
          <Card>
            <CardContent className=\"p-4\">
              <div className=\"flex items-center gap-3\">
                <div className=\"p-2 bg-yellow-100 dark:bg-yellow-900 rounded-lg\">
                  <Home className=\"w-4 h-4 text-yellow-600 dark:text-yellow-400\" />
                </div>
                <div>
                  <p className=\"text-xs text-muted-foreground\">Portfolio Value</p>
                  <p className=\"text-lg font-semibold\">
                    ${portfolioData.reduce((sum, p) => sum + p.totalValue, 0).toLocaleString()}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.3 }}
        >
          <Card>
            <CardContent className=\"p-4\">
              <div className=\"flex items-center gap-3\">
                <div className=\"p-2 bg-purple-100 dark:bg-purple-900 rounded-lg\">
                  <Activity className=\"w-4 h-4 text-purple-600 dark:text-purple-400\" />
                </div>
                <div>
                  <p className=\"text-xs text-muted-foreground\">Avg Occupancy</p>
                  <p className=\"text-lg font-semibold\">
                    {propertyMetrics.length > 0 ? 
                      ((propertyMetrics.reduce((sum, m) => sum + m.occupancyRate, 0) / propertyMetrics.length) * 100).toFixed(0) : 
                      '0'
                    }%
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Charts Tabs */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
      >
        <Tabs value={activeTab} onValueChange={setActiveTab} className=\"space-y-4\">
          <TabsList className=\"grid w-full grid-cols-4\">
            <TabsTrigger value=\"performance\">Performance</TabsTrigger>
            <TabsTrigger value=\"cashflow\">Cash Flow</TabsTrigger>
            <TabsTrigger value=\"portfolio\">Portfolio</TabsTrigger>
            <TabsTrigger value=\"market\">Market</TabsTrigger>
          </TabsList>

          {/* Performance Tab */}
          <TabsContent value=\"performance\" className=\"space-y-4\">
            <div className=\"grid grid-cols-1 lg:grid-cols-2 gap-4\">
              <Card className=\"relative\">
                {isLoading && <LoadingOverlay />}
                <CardHeader>
                  <CardTitle className=\"flex items-center gap-2\">
                    <BarChart3 className=\"w-4 h-4\" />
                    ROI & Cap Rate Trends
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width=\"100%\" height={300}>
                    <LineChart data={performanceData}>
                      <CartesianGrid strokeDasharray=\"3 3\" stroke=\"#E5E7EB\" />
                      <XAxis dataKey=\"month\" stroke=\"#6B7280\" />
                      <YAxis stroke=\"#6B7280\" />
                      <Tooltip content={<CustomTooltip />} />
                      <Legend />
                      <Line 
                        type=\"monotone\" 
                        dataKey=\"roi\" 
                        stroke={COLORS.primary} 
                        strokeWidth={2}
                        name=\"ROI (%)\"
                        dot={{ fill: COLORS.primary, strokeWidth: 2 }}
                      />
                      <Line 
                        type=\"monotone\" 
                        dataKey=\"capRate\" 
                        stroke={COLORS.secondary} 
                        strokeWidth={2}
                        name=\"Cap Rate (%)\"
                        dot={{ fill: COLORS.secondary, strokeWidth: 2 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card className=\"relative\">
                {isLoading && <LoadingOverlay />}
                <CardHeader>
                  <CardTitle className=\"flex items-center gap-2\">
                    <Activity className=\"w-4 h-4\" />
                    Occupancy Rate
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width=\"100%\" height={300}>
                    <AreaChart data={performanceData}>
                      <CartesianGrid strokeDasharray=\"3 3\" stroke=\"#E5E7EB\" />
                      <XAxis dataKey=\"month\" stroke=\"#6B7280\" />
                      <YAxis stroke=\"#6B7280\" domain={[0, 100]} />
                      <Tooltip content={<CustomTooltip />} />
                      <Area 
                        type=\"monotone\" 
                        dataKey=\"occupancy\" 
                        stroke={COLORS.accent} 
                        fill={COLORS.accent}
                        fillOpacity={0.3}
                        name=\"Occupancy (%)\"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Cash Flow Tab */}
          <TabsContent value=\"cashflow\" className=\"space-y-4\">
            <div className=\"grid grid-cols-1 lg:grid-cols-2 gap-4\">
              <Card className=\"relative\">
                {isLoading && <LoadingOverlay />}
                <CardHeader>
                  <CardTitle className=\"flex items-center gap-2\">
                    <DollarSign className=\"w-4 h-4\" />
                    Monthly Cash Flow Analysis
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width=\"100%\" height={300}>
                    <BarChart data={cashFlowData}>
                      <CartesianGrid strokeDasharray=\"3 3\" stroke=\"#E5E7EB\" />
                      <XAxis dataKey=\"month\" stroke=\"#6B7280\" />
                      <YAxis stroke=\"#6B7280\" />
                      <Tooltip content={<CustomTooltip />} />
                      <Legend />
                      <Bar dataKey=\"rent\" fill={COLORS.secondary} name=\"Monthly Rent\" />
                      <Bar dataKey=\"expenses\" fill={COLORS.warning} name=\"Operating Expenses\" />
                      <Bar dataKey=\"netIncome\" fill={COLORS.primary} name=\"Net Income\" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card className=\"relative\">
                {isLoading && <LoadingOverlay />}
                <CardHeader>
                  <CardTitle className=\"flex items-center gap-2\">
                    <TrendingUp className=\"w-4 h-4\" />
                    Cash Flow Trend
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width=\"100%\" height={300}>
                    <LineChart data={cashFlowData}>
                      <CartesianGrid strokeDasharray=\"3 3\" stroke=\"#E5E7EB\" />
                      <XAxis dataKey=\"month\" stroke=\"#6B7280\" />
                      <YAxis stroke=\"#6B7280\" />
                      <Tooltip content={<CustomTooltip />} />
                      <Legend />
                      <Line 
                        type=\"monotone\" 
                        dataKey=\"cashFlow\" 
                        stroke={COLORS.primary} 
                        strokeWidth={3}
                        name=\"Cash Flow\"
                        dot={{ fill: COLORS.primary, strokeWidth: 2, r: 4 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Portfolio Tab */}
          <TabsContent value=\"portfolio\" className=\"space-y-4\">
            <div className=\"grid grid-cols-1 lg:grid-cols-2 gap-4\">
              <Card className=\"relative\">
                {isLoading && <LoadingOverlay />}
                <CardHeader>
                  <CardTitle className=\"flex items-center gap-2\">
                    <PieChartIcon className=\"w-4 h-4\" />
                    Portfolio Distribution by Value
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width=\"100%\" height={300}>
                    <PieChart>
                      <Pie
                        data={portfolioDistribution}
                        cx=\"50%\"
                        cy=\"50%\"
                        outerRadius={100}
                        fill=\"#8884d8\"
                        dataKey=\"value\"
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      >
                        {portfolioDistribution.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip 
                        formatter={(value: number) => [`$${value.toLocaleString()}`, 'Value']}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card className=\"relative\">
                {isLoading && <LoadingOverlay />}
                <CardHeader>
                  <CardTitle className=\"flex items-center gap-2\">
                    <Home className=\"w-4 h-4\" />
                    Property Count by Type
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width=\"100%\" height={300}>
                    <BarChart data={portfolioDistribution} layout=\"horizontal\">
                      <CartesianGrid strokeDasharray=\"3 3\" stroke=\"#E5E7EB\" />
                      <XAxis type=\"number\" stroke=\"#6B7280\" />
                      <YAxis dataKey=\"name\" type=\"category\" stroke=\"#6B7280\" width={80} />
                      <Tooltip content={<CustomTooltip />} />
                      <Bar dataKey=\"count\" fill={COLORS.secondary} name=\"Property Count\" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>

            {/* Portfolio Performance Table */}
            <Card>
              <CardHeader>
                <CardTitle>Portfolio Performance Summary</CardTitle>
              </CardHeader>
              <CardContent>
                <div className=\"overflow-x-auto\">
                  <table className=\"w-full\">
                    <thead>
                      <tr className=\"border-b\">
                        <th className=\"text-left p-2\">Property Type</th>
                        <th className=\"text-right p-2\">Count</th>
                        <th className=\"text-right p-2\">Total Value</th>
                        <th className=\"text-right p-2\">Monthly Income</th>
                        <th className=\"text-center p-2\">Performance</th>
                      </tr>
                    </thead>
                    <tbody>
                      {portfolioData.map((item, index) => (
                        <tr key={index} className=\"border-b\">
                          <td className=\"p-2 font-medium\">{item.propertyType}</td>
                          <td className=\"text-right p-2\">{item.count}</td>
                          <td className=\"text-right p-2\">${item.totalValue.toLocaleString()}</td>
                          <td className=\"text-right p-2\">${item.monthlyIncome.toLocaleString()}</td>
                          <td className=\"text-center p-2\">
                            <Badge 
                              variant={item.performance === 'excellent' ? 'default' : 
                                      item.performance === 'good' ? 'secondary' : 
                                      item.performance === 'average' ? 'outline' : 'destructive'}
                            >
                              {item.performance}
                            </Badge>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Market Tab */}
          <TabsContent value=\"market\" className=\"space-y-4\">
            <div className=\"grid grid-cols-1 lg:grid-cols-2 gap-4\">
              <Card className=\"relative\">
                {isLoading && <LoadingOverlay />}
                <CardHeader>
                  <CardTitle className=\"flex items-center gap-2\">
                    <TrendingUp className=\"w-4 h-4\" />
                    Market Price Trends
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width=\"100%\" height={300}>
                    <LineChart data={marketTrends}>
                      <CartesianGrid strokeDasharray=\"3 3\" stroke=\"#E5E7EB\" />
                      <XAxis dataKey=\"month\" stroke=\"#6B7280\" />
                      <YAxis stroke=\"#6B7280\" />
                      <Tooltip content={<CustomTooltip />} />
                      <Legend />
                      <Line 
                        type=\"monotone\" 
                        dataKey=\"price\" 
                        stroke={COLORS.primary} 
                        strokeWidth={2}
                        name=\"Avg Price\"
                        dot={{ fill: COLORS.primary, strokeWidth: 2 }}
                      />
                      <Line 
                        type=\"monotone\" 
                        dataKey=\"pricePerSqft\" 
                        stroke={COLORS.accent} 
                        strokeWidth={2}
                        name=\"Price/SqFt\"
                        dot={{ fill: COLORS.accent, strokeWidth: 2 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card className=\"relative\">
                {isLoading && <LoadingOverlay />}
                <CardHeader>
                  <CardTitle className=\"flex items-center gap-2\">
                    <BarChart3 className=\"w-4 h-4\" />
                    Sales Volume & Days on Market
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width=\"100%\" height={300}>
                    <BarChart data={marketTrends}>
                      <CartesianGrid strokeDasharray=\"3 3\" stroke=\"#E5E7EB\" />
                      <XAxis dataKey=\"month\" stroke=\"#6B7280\" />
                      <YAxis stroke=\"#6B7280\" />
                      <Tooltip content={<CustomTooltip />} />
                      <Legend />
                      <Bar dataKey=\"volume\" fill={COLORS.secondary} name=\"Sales Volume\" />
                      <Bar dataKey=\"dom\" fill={COLORS.warning} name=\"Days on Market\" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </motion.div>
    </div>
  );
}

export default PropertyCharts;", "original_text": "", "replace_all": false}]