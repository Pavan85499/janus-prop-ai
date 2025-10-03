import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Calendar, TrendingUp, DollarSign, Building2, Users, Activity, BarChart3, PieChart, LineChart } from 'lucide-react';
import { AppLayout } from '@/components/layout/AppLayout';
import backendService from '@/lib/backendService';
import { LineChart as RLineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, Area, AreaChart, PieChart as RPieChart, Pie, Cell, BarChart, Bar } from 'recharts';

const Analytics = () => {
  const [timeRange, setTimeRange] = useState('30d');
  const [selectedMetric, setSelectedMetric] = useState('overview');
  const [roiSeries, setRoiSeries] = useState<{ period: string; avg_roi: number; count: number }[]>([]);
  const [velocitySeries, setVelocitySeries] = useState<{ period: string; avg_days_to_close: number; count: number }[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [portfolioType, setPortfolioType] = useState<{ label: string; count: number; total_value: number; share: number }[]>([]);
  const [portfolioLocation, setPortfolioLocation] = useState<{ label: string; count: number; total_value: number; share: number }[]>([]);

  useEffect(() => {
    const months = timeRange === '7d' ? 1 : timeRange === '30d' ? 1 : timeRange === '90d' ? 3 : 12;
    let canceled = false;
    setLoading(true);
    setError(null);
    Promise.all([
      backendService.getROITrends(months),
      backendService.getDealVelocity(months),
    ])
      .then(([roi, vel]) => {
        if (canceled) return;
        setRoiSeries(roi.series);
        setVelocitySeries(vel.series);
      })
      .catch((e) => {
        if (canceled) return;
        setError(e?.message || 'Failed to load analytics');
      })
      .finally(() => {
        if (canceled) return;
        setLoading(false);
      });
    return () => {
      canceled = true;
    };
  }, [timeRange]);

  useEffect(() => {
    let canceled = false;
    backendService
      .getPortfolioBreakdown('type')
      .then((res) => {
        if (canceled) return;
        setPortfolioType(res.items);
      })
      .catch(() => {})
    backendService
      .getPortfolioBreakdown('location')
      .then((res) => {
        if (canceled) return;
        setPortfolioLocation(res.items);
      })
      .catch(() => {})
    return () => {
      canceled = true;
    };
  }, []);

  // Mock data - replace with actual API calls
  const analyticsData = {
    overview: {
      totalValue: 12500000,
      monthlyGrowth: 12.5,
      activeDeals: 47,
      completedDeals: 23,
      totalAgents: 8,
      activeAgents: 6
    },
    performance: [
      { metric: 'ROI', value: '24.3%', change: '+5.2%', trend: 'up' },
      { metric: 'Deal Velocity', value: '18 days', change: '-3 days', trend: 'up' },
      { metric: 'Conversion Rate', value: '68%', change: '+12%', trend: 'up' },
      { metric: 'Cost per Lead', value: '$450', change: '-$25', trend: 'up' }
    ],
    portfolio: [
      { name: 'Residential', value: 45, color: 'bg-blue-500' },
      { name: 'Commercial', value: 30, color: 'bg-green-500' },
      { name: 'Industrial', value: 15, color: 'bg-yellow-500' },
      { name: 'Mixed-Use', value: 10, color: 'bg-purple-500' }
    ],
    recentActivity: [
      { action: 'New deal closed', property: '123 Main St', value: '$2.5M', time: '2 hours ago' },
      { action: 'Agent completed task', agent: 'Eden', task: 'Market analysis', time: '4 hours ago' },
      { action: 'Property added', property: '456 Oak Ave', value: '$1.8M', time: '6 hours ago' },
      { action: 'Portfolio updated', portfolio: 'Q4 2024', change: '+$500K', time: '1 day ago' }
    ]
  };

  const StatCard = ({ title, value, change, icon: Icon, trend }: { title: string; value: string | number; change: string; icon: React.ElementType; trend: string; }) => (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <p className={`text-xs ${trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
          {change} from last month
        </p>
      </CardContent>
    </Card>
  );

  return (
    <AppLayout>
      <div className="flex-1 space-y-6 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Analytics</h2>
          <p className="text-muted-foreground">
            Comprehensive insights into your real estate investment performance
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Select time range" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7d">Last 7 days</SelectItem>
              <SelectItem value="30d">Last 30 days</SelectItem>
              <SelectItem value="90d">Last 90 days</SelectItem>
              <SelectItem value="1y">Last year</SelectItem>
            </SelectContent>
          </Select>
          <Button>
            <Calendar className="mr-2 h-4 w-4" />
            Export Report
          </Button>
        </div>
      </div>

      <Tabs value={selectedMetric} onValueChange={setSelectedMetric} className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="portfolio">Portfolio</TabsTrigger>
          <TabsTrigger value="agents">Agents</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <StatCard
              title="Total Portfolio Value"
              value={`$${(analyticsData.overview.totalValue / 1000000).toFixed(1)}M`}
              change="+12.5%"
              icon={DollarSign}
              trend="up"
            />
            <StatCard
              title="Active Deals"
              value={analyticsData.overview.activeDeals}
              change="+8"
              icon={Building2}
              trend="up"
            />
            <StatCard
              title="Completed Deals"
              value={analyticsData.overview.completedDeals}
              change="+5"
              icon={TrendingUp}
              trend="up"
            />
            <StatCard
              title="Active Agents"
              value={`${analyticsData.overview.activeAgents}/${analyticsData.overview.totalAgents}`}
              change="+2"
              icon={Users}
              trend="up"
            />
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Portfolio Distribution</CardTitle>
                <CardDescription>Asset allocation across property types</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {analyticsData.portfolio.map((item, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <div className={`w-3 h-3 rounded-full ${item.color}`} />
                        <span className="text-sm font-medium">{item.name}</span>
                      </div>
                      <span className="text-sm text-muted-foreground">{item.value}%</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
                <CardDescription>Latest updates across the platform</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {analyticsData.recentActivity.map((activity, index) => (
                    <div key={index} className="flex items-start space-x-3">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mt-2" />
                      <div className="flex-1 space-y-1">
                        <p className="text-sm font-medium">{activity.action}</p>
                        <p className="text-xs text-muted-foreground">
                          {activity.property || activity.agent || activity.portfolio} • {activity.time}
                        </p>
                      </div>
                      <Badge variant="secondary">{activity.value || activity.change}</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="performance" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {analyticsData.performance.map((metric, index) => (
              <StatCard
                key={index}
                title={metric.metric}
                value={metric.value}
                change={metric.change}
                icon={BarChart3}
                trend={metric.trend}
              />
            ))}
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>ROI Trends</CardTitle>
                <CardDescription>Return on investment over time</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  {error ? (
                    <div className="text-sm text-red-600">{error}</div>
                  ) : (
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={roiSeries} margin={{ top: 16, right: 16, left: 0, bottom: 0 }}>
                        <defs>
                          <linearGradient id="roiColor" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3}/>
                            <stop offset="95%" stopColor="#22c55e" stopOpacity={0}/>
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" strokeOpacity={0.15} />
                        <XAxis dataKey="period" tick={{ fontSize: 12 }} />
                        <YAxis tickFormatter={(v) => `${Math.round(v * 100)}%`} width={48} />
                        <Tooltip formatter={(v: number) => `${Math.round(v * 1000) / 10}%`} labelClassName="text-xs" />
                        <Legend />
                        <Area type="monotone" dataKey="avg_roi" stroke="#16a34a" fillOpacity={1} fill="url(#roiColor)" name="Avg ROI" />
                      </AreaChart>
                    </ResponsiveContainer>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Deal Velocity</CardTitle>
                <CardDescription>Average time from listing to closing</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  {error ? (
                    <div className="text-sm text-red-600">{error}</div>
                  ) : (
                    <ResponsiveContainer width="100%" height="100%">
                      <RLineChart data={velocitySeries} margin={{ top: 16, right: 16, left: 0, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" strokeOpacity={0.15} />
                        <XAxis dataKey="period" tick={{ fontSize: 12 }} />
                        <YAxis width={48} />
                        <Tooltip labelClassName="text-xs" />
                        <Legend />
                        <Line type="monotone" dataKey="avg_days_to_close" stroke="#2563eb" dot={false} name="Avg Days" />
                      </RLineChart>
                    </ResponsiveContainer>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="portfolio" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>By Property Type</CardTitle>
                <CardDescription>Distribution of portfolio value</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[360px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <RPieChart>
                      <Tooltip formatter={(v: number, name: string) => name === 'share' ? `${Math.round((v as number) * 1000) / 10}%` : v} />
                      <Legend />
                      <Pie data={portfolioType} dataKey="share" nameKey="label" outerRadius={120} label={(d) => `${d.label}: ${Math.round(d.share * 1000) / 10}%`}>
                        {portfolioType.map((_, i) => (
                          <Cell key={i} fill={["#3b82f6", "#22c55e", "#f59e0b", "#a855f7", "#ef4444"][i % 5]} />
                        ))}
                      </Pie>
                    </RPieChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Top Locations</CardTitle>
                <CardDescription>Average portfolio value by market</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[360px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={portfolioLocation} margin={{ top: 16, right: 16, left: 0, bottom: 32 }}>
                      <CartesianGrid strokeDasharray="3 3" strokeOpacity={0.15} />
                      <XAxis dataKey="label" interval={0} angle={-20} textAnchor="end" height={60} tick={{ fontSize: 12 }} />
                      <YAxis tickFormatter={(v) => `$${(v/1_000_000).toFixed(1)}M`} width={64} />
                      <Tooltip formatter={(v: number, name: string) => name === 'total_value' ? `$${(v as number).toLocaleString()}` : v} />
                      <Legend />
                      <Bar dataKey="total_value" name="Total Value" fill="#2563eb" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="agents" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <Card>
              <CardHeader>
                <CardTitle>Agent Performance</CardTitle>
                <CardDescription>Task completion and efficiency metrics</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Tasks Completed</span>
                    <span className="font-medium">1,247</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Success Rate</span>
                    <span className="font-medium text-green-600">94.2%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Avg. Response Time</span>
                    <span className="font-medium">2.3 min</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Agent Utilization</CardTitle>
                <CardDescription>Current workload distribution</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Eden</span>
                    <Badge variant="default">Active</Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Atlas</span>
                    <Badge variant="secondary">Idle</Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Nova</span>
                    <Badge variant="default">Active</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>AI Insights</CardTitle>
                <CardDescription>Machine learning recommendations</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <p className="text-sm">• Optimize deal flow in Q4</p>
                  <p className="text-sm">• Focus on commercial properties</p>
                  <p className="text-sm">• Increase agent capacity by 20%</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
      </div>
    </AppLayout>
  );
};

export default Analytics;
