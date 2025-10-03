import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { 
  Plus, 
  Briefcase, 
  TrendingUp, 
  TrendingDown,
  DollarSign,
  Search,
  Filter,
  RefreshCw,
  Eye,
  Edit,
  Trash2,
  PieChart,
  BarChart3,
  Target,
  Calendar,
  Users,
  Building2,
  Map,
  Navigation
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { AppLayout } from "@/components/layout/AppLayout";
import { useRealEstateAPIs } from "@/hooks/useRealEstateAPIs";
import PortfolioMap, { PortfolioMapMarker } from "@/components/dashboard/PortfolioMap";

interface Portfolio {
  id: string;
  name: string;
  description: string;
  type: 'residential' | 'commercial' | 'mixed' | 'reit';
  status: 'active' | 'inactive' | 'liquidating';
  totalValue: number;
  totalInvestment: number;
  currentROI: number;
  targetROI: number;
  properties: number;
  monthlyIncome: number;
  annualIncome: number;
  expenses: number;
  netIncome: number;
  cashFlow: number;
  occupancyRate: number;
  averageCapRate: number;
  riskLevel: 'low' | 'medium' | 'high';
  created_at: string;
  updated_at: string;
  lastPerformanceUpdate: string;
}

interface PortfolioPerformance {
  period: string;
  roi: number;
  appreciation: number;
  income: number;
  totalReturn: number;
}

const PORTFOLIO_TYPES = [
  { value: "residential", label: "Residential", description: "Single and multi-family properties" },
  { value: "commercial", label: "Commercial", description: "Office, retail, and industrial properties" },
  { value: "mixed", label: "Mixed Use", description: "Combination of residential and commercial" },
  { value: "reit", label: "REIT", description: "Real Estate Investment Trust" },
];

const RISK_LEVELS = [
  { value: "low", label: "Low Risk", description: "Conservative investments" },
  { value: "medium", label: "Medium Risk", description: "Balanced approach" },
  { value: "high", label: "High Risk", description: "Aggressive growth strategy" },
];

export default function Portfolios() {
  const { toast } = useToast();
  
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [performance, setPerformance] = useState<PortfolioPerformance[]>([]);
  const [loading, setLoading] = useState(false);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [selectedPortfolio, setSelectedPortfolio] = useState<Portfolio | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [typeFilter, setTypeFilter] = useState<string>("all");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  
  const [newPortfolio, setNewPortfolio] = useState({
    name: "",
    description: "",
    type: "",
    targetROI: 0,
    riskLevel: "",
  });

  // Real-time properties for map view
  const {
    properties: liveProperties,
    loading: propsLoading,
    isConnected: propsConnected,
    lastUpdated: propsUpdated,
    refreshProperties,
    testConnection
  } = useRealEstateAPIs(true, 60000);

  const [userLocation, setUserLocation] = useState<{ lat: number; lng: number } | null>(null);
  const [locError, setLocError] = useState<string | null>(null);

  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => setUserLocation({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
        () => setLocError("Location permission denied")
      );
    } else {
      setLocError("Geolocation not supported");
    }
  }, []);

  const fallbackCenter = () => {
    // Use first live property with coordinates or default to New York
    const p = liveProperties.find(p => p.latitude && p.longitude);
    if (p) return { lat: Number(p.latitude), lng: Number(p.longitude) };
    return { lat: 40.7128, lng: -74.0060 };
  };

  const mapCenter = userLocation || fallbackCenter();

  const distanceKm = (a: { lat: number; lng: number }, b: { lat: number; lng: number }) => {
    const toRad = (x: number) => (x * Math.PI) / 180;
    const R = 6371;
    const dLat = toRad(b.lat - a.lat);
    const dLon = toRad(b.lng - a.lng);
    const lat1 = toRad(a.lat);
    const lat2 = toRad(b.lat);
    const sinDLat = Math.sin(dLat / 2);
    const sinDLon = Math.sin(dLon / 2);
    const c = 2 * Math.asin(Math.sqrt(sinDLat * sinDLat + Math.cos(lat1) * Math.cos(lat2) * sinDLon * sinDLon));
    return R * c;
  };

  const nearest = userLocation
    ? [...liveProperties]
        .filter(p => p.latitude && p.longitude)
        .map(p => ({
          id: p.id,
          address: p.address,
          lat: p.latitude as number,
          lng: p.longitude as number,
          distance: distanceKm(userLocation, { lat: p.latitude as number, lng: p.longitude as number })
        }))
        .sort((a, b) => a.distance - b.distance)
        .slice(0, 10)
    : [];

  // Load portfolios
  useEffect(() => {
    loadPortfolios();
    loadPerformance();
  }, []);

  const loadPortfolios = async () => {
    try {
      setLoading(true);
      // Mock data for now
      const mockPortfolios: Portfolio[] = [
        {
          id: "1",
          name: "Austin Residential Portfolio",
          description: "High-growth residential properties in Austin metro area",
          type: "residential",
          status: "active",
          totalValue: 2500000,
          totalInvestment: 2000000,
          currentROI: 12.5,
          targetROI: 15.0,
          properties: 8,
          monthlyIncome: 18500,
          annualIncome: 222000,
          expenses: 45000,
          netIncome: 177000,
          cashFlow: 14750,
          occupancyRate: 95.5,
          averageCapRate: 7.1,
          riskLevel: "medium",
          created_at: "2024-01-15T00:00:00Z",
          updated_at: new Date().toISOString(),
          lastPerformanceUpdate: new Date().toISOString(),
        },
        {
          id: "2",
          name: "Houston Commercial REIT",
          description: "Diversified commercial real estate investment trust",
          type: "reit",
          status: "active",
          totalValue: 5000000,
          totalInvestment: 4500000,
          currentROI: 8.8,
          targetROI: 10.0,
          properties: 12,
          monthlyIncome: 32000,
          annualIncome: 384000,
          expenses: 120000,
          netIncome: 264000,
          cashFlow: 22000,
          occupancyRate: 88.2,
          averageCapRate: 5.3,
          riskLevel: "low",
          created_at: "2023-06-20T00:00:00Z",
          updated_at: new Date().toISOString(),
          lastPerformanceUpdate: new Date().toISOString(),
        },
        {
          id: "3",
          name: "Dallas Mixed-Use Development",
          description: "Urban mixed-use development with retail and residential",
          type: "mixed",
          status: "active",
          totalValue: 7500000,
          totalInvestment: 6000000,
          currentROI: 18.2,
          targetROI: 20.0,
          properties: 5,
          monthlyIncome: 45000,
          annualIncome: 540000,
          expenses: 180000,
          netIncome: 360000,
          cashFlow: 30000,
          occupancyRate: 92.8,
          averageCapRate: 4.8,
          riskLevel: "high",
          created_at: "2023-03-10T00:00:00Z",
          updated_at: new Date().toISOString(),
          lastPerformanceUpdate: new Date().toISOString(),
        }
      ];
      setPortfolios(mockPortfolios);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load portfolios",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const loadPerformance = async () => {
    // Mock performance data
    const mockPerformance: PortfolioPerformance[] = [
      { period: "Q1 2024", roi: 3.2, appreciation: 2.1, income: 1.1, totalReturn: 3.2 },
      { period: "Q2 2024", roi: 2.8, appreciation: 1.8, income: 1.0, totalReturn: 2.8 },
      { period: "Q3 2024", roi: 3.5, appreciation: 2.3, income: 1.2, totalReturn: 3.5 },
      { period: "Q4 2024", roi: 4.1, appreciation: 2.7, income: 1.4, totalReturn: 4.1 },
    ];
    setPerformance(mockPerformance);
  };

  const createPortfolio = async () => {
    try {
      setLoading(true);
      const portfolio: Portfolio = {
        id: Date.now().toString(),
        name: newPortfolio.name,
        description: newPortfolio.description,
        type: (newPortfolio.type as Portfolio['type']) || 'residential',
        status: "active",
        totalValue: 0,
        totalInvestment: 0,
        currentROI: 0,
        targetROI: newPortfolio.targetROI,
        properties: 0,
        monthlyIncome: 0,
        annualIncome: 0,
        expenses: 0,
        netIncome: 0,
        cashFlow: 0,
        occupancyRate: 0,
        averageCapRate: 0,
        riskLevel: (newPortfolio.riskLevel as Portfolio['riskLevel']) || 'medium',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        lastPerformanceUpdate: new Date().toISOString(),
      };

      setPortfolios(prev => [portfolio, ...prev]);
      setShowCreateDialog(false);
      setNewPortfolio({
        name: "",
        description: "",
        type: "",
        targetROI: 0,
        riskLevel: "",
      });

      toast({
        title: "Success",
        description: "Portfolio created successfully",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create portfolio",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-success/20 text-success border-success/30';
      case 'inactive': return 'bg-muted/20 text-muted-foreground border-muted/30';
      case 'liquidating': return 'bg-warning/20 text-warning border-warning/30';
      default: return 'bg-muted/20 text-muted-foreground border-muted/30';
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'low': return 'bg-success/20 text-success border-success/30';
      case 'medium': return 'bg-warning/20 text-warning border-warning/30';
      case 'high': return 'bg-destructive/20 text-destructive border-destructive/30';
      default: return 'bg-muted/20 text-muted-foreground border-muted/30';
    }
  };

  const filteredPortfolios = portfolios.filter(portfolio => {
    const matchesSearch = portfolio.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         portfolio.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = typeFilter === "all" || portfolio.type === typeFilter;
    const matchesStatus = statusFilter === "all" || portfolio.status === statusFilter;
    return matchesSearch && matchesType && matchesStatus;
  });

  const totalPortfolioValue = portfolios.reduce((sum, p) => sum + p.totalValue, 0);
  const totalProperties = portfolios.reduce((sum, p) => sum + p.properties, 0);
  const avgROI = portfolios.length > 0 ? portfolios.reduce((sum, p) => sum + p.currentROI, 0) / portfolios.length : 0;
  const totalMonthlyIncome = portfolios.reduce((sum, p) => sum + p.monthlyIncome, 0);

  return (
    <AppLayout>
      <div className="min-h-screen bg-gradient-to-br from-background to-muted">
      {/* Header */}
      <div className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold">Portfolios</h1>
              <p className="text-muted-foreground mt-1">
                Manage your real estate investment portfolios
              </p>
            </div>
            <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
              <DialogTrigger asChild>
                <Button className="flex items-center gap-2">
                  <Plus className="w-4 h-4" />
                  Create Portfolio
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-md">
                <DialogHeader>
                  <DialogTitle>Create New Portfolio</DialogTitle>
                  <DialogDescription>
                    Create a new investment portfolio
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Portfolio Name</Label>
                    <Input
                      id="name"
                      value={newPortfolio.name}
                      onChange={(e) => setNewPortfolio(prev => ({ ...prev, name: e.target.value }))}
                      placeholder="Enter portfolio name"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="description">Description</Label>
                    <Textarea
                      id="description"
                      value={newPortfolio.description}
                      onChange={(e) => setNewPortfolio(prev => ({ ...prev, description: e.target.value }))}
                      placeholder="Describe your investment strategy..."
                      rows={3}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="type">Portfolio Type</Label>
                    <Select value={newPortfolio.type} onValueChange={(value) => setNewPortfolio(prev => ({ ...prev, type: value }))}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select portfolio type" />
                      </SelectTrigger>
                      <SelectContent>
                        {PORTFOLIO_TYPES.map((type) => (
                          <SelectItem key={type.value} value={type.value}>
                            <div>
                              <div className="font-medium">{type.label}</div>
                              <div className="text-sm text-muted-foreground">{type.description}</div>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="targetROI">Target ROI (%)</Label>
                      <Input
                        id="targetROI"
                        type="number"
                        value={newPortfolio.targetROI}
                        onChange={(e) => setNewPortfolio(prev => ({ ...prev, targetROI: Number(e.target.value) }))}
                        placeholder="12.0"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="riskLevel">Risk Level</Label>
                      <Select value={newPortfolio.riskLevel} onValueChange={(value) => setNewPortfolio(prev => ({ ...prev, riskLevel: value }))}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select risk level" />
                        </SelectTrigger>
                        <SelectContent>
                          {RISK_LEVELS.map((risk) => (
                            <SelectItem key={risk.value} value={risk.value}>
                              <div>
                                <div className="font-medium">{risk.label}</div>
                                <div className="text-sm text-muted-foreground">{risk.description}</div>
                              </div>
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <div className="flex justify-end space-x-2">
                    <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                      Cancel
                    </Button>
                    <Button onClick={createPortfolio} disabled={loading}>
                      {loading ? "Creating..." : "Create Portfolio"}
                    </Button>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <Briefcase className="w-5 h-5 text-primary" />
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Portfolios</p>
                  <p className="text-2xl font-bold">{portfolios.length}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <DollarSign className="w-5 h-5 text-success" />
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Value</p>
                  <p className="text-2xl font-bold">${(totalPortfolioValue / 1000000).toFixed(1)}M</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <Building2 className="w-5 h-5 text-warning" />
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Properties</p>
                  <p className="text-2xl font-bold">{totalProperties}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <TrendingUp className="w-5 h-5 text-info" />
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Avg ROI</p>
                  <p className="text-2xl font-bold">{avgROI.toFixed(1)}%</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Performance Overview */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5" />
              Portfolio Performance
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {performance.map((perf) => (
                <div key={perf.period} className="text-center p-4 border rounded-lg">
                  <div className="text-sm font-medium text-muted-foreground">{perf.period}</div>
                  <div className="text-2xl font-bold text-success">{perf.totalReturn}%</div>
                  <div className="text-xs text-muted-foreground">
                    ROI: {perf.roi}% | Appreciation: {perf.appreciation}% | Income: {perf.income}%
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Real-time Map View */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Map className="w-5 h-5" />
              Portfolio Map (Real-time)
              {propsUpdated && (
                <span className="text-sm font-normal text-muted-foreground">• Updated {propsUpdated.toLocaleTimeString()}</span>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col gap-4">
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" onClick={refreshProperties} disabled={propsLoading}>
                  <RefreshCw className={`w-4 h-4 ${propsLoading ? 'animate-spin' : ''}`} />
                </Button>
                {!propsConnected && (
                  <Badge variant="destructive" className="text-xs">Offline</Badge>
                )}
                {userLocation ? (
                  <Badge variant="outline" className="text-xs">
                    <Navigation className="w-3 h-3 mr-1" />
                    {userLocation.lat.toFixed(3)}, {userLocation.lng.toFixed(3)}
                  </Badge>
                ) : (
                  <span className="text-xs text-muted-foreground">{locError || 'Detecting location...'}</span>
                )}
              </div>
              <div className="h-64 w-full bg-muted border border-border rounded-lg">
                <PortfolioMap
                  center={mapCenter}
                  userPosition={userLocation}
                  markers={(userLocation ? (nearest as any[]) : liveProperties.filter(p => p.latitude && p.longitude).slice(0, 50).map(p => ({
                    id: p.id,
                    address: p.address,
                    lat: Number(p.latitude),
                    lng: Number(p.longitude),
                    distance: 0
                  }))).map((p: any): PortfolioMapMarker => ({
                    id: p.id,
                    position: { lat: p.lat, lng: p.lng },
                    label: p.address,
                    subtitle: p.distance ? `${p.distance.toFixed(1)} km away` : undefined
                  }))}
                  height={320}
                />
              </div>
              {!userLocation && (
                <p className="text-xs text-muted-foreground">{locError ? `${locError}. Showing nearby market center.` : 'Detecting location... Showing nearby market center if unavailable.'}</p>
              )}
              {userLocation && nearest.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium mb-2">Nearest Properties</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    {nearest.map(p => (
                      <div key={p.id} className="p-3 border rounded-lg text-sm">
                        <div className="font-medium truncate">{p.address}</div>
                        <div className="text-muted-foreground">{p.distance.toFixed(1)} km away</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Filters */}
        <div className="flex items-center space-x-4 mb-6">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
              <Input
                placeholder="Search portfolios..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
          <Select value={typeFilter} onValueChange={setTypeFilter}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="Filter by type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
              {PORTFOLIO_TYPES.map((type) => (
                <SelectItem key={type.value} value={type.value}>
                  {type.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="Filter by status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="active">Active</SelectItem>
              <SelectItem value="inactive">Inactive</SelectItem>
              <SelectItem value="liquidating">Liquidating</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline" onClick={loadPortfolios}>
            <RefreshCw className="w-4 h-4" />
          </Button>
        </div>

        {/* Portfolios Table */}
        <Card>
          <CardHeader>
            <CardTitle>Portfolios</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                <p className="mt-2 text-muted-foreground">Loading portfolios...</p>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Portfolio</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Value</TableHead>
                    <TableHead>ROI</TableHead>
                    <TableHead>Properties</TableHead>
                    <TableHead>Risk</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredPortfolios.map((portfolio) => (
                    <TableRow key={portfolio.id}>
                      <TableCell>
                        <div>
                          <div className="font-medium">{portfolio.name}</div>
                          <div className="text-sm text-muted-foreground">{portfolio.description}</div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">
                          {PORTFOLIO_TYPES.find(t => t.value === portfolio.type)?.label}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Badge className={getStatusColor(portfolio.status)}>
                          {portfolio.status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div>
                          <div className="font-medium">${(portfolio.totalValue / 1000000).toFixed(1)}M</div>
                          <div className="text-sm text-muted-foreground">
                            Invested: ${(portfolio.totalInvestment / 1000000).toFixed(1)}M
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center space-x-1">
                          {portfolio.currentROI >= portfolio.targetROI ? (
                            <TrendingUp className="w-4 h-4 text-success" />
                          ) : (
                            <TrendingDown className="w-4 h-4 text-destructive" />
                          )}
                          <div>
                            <div className="font-medium">{portfolio.currentROI}%</div>
                            <div className="text-sm text-muted-foreground">
                              Target: {portfolio.targetROI}%
                            </div>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="text-center">
                          <div className="font-medium">{portfolio.properties}</div>
                          <div className="text-sm text-muted-foreground">
                            {portfolio.occupancyRate}% occupied
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge className={getRiskColor(portfolio.riskLevel)}>
                          {portfolio.riskLevel}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center space-x-2">
                          <Button size="sm" variant="outline">
                            <Eye className="w-3 h-3" />
                          </Button>
                          <Button size="sm" variant="outline">
                            <Edit className="w-3 h-3" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>
      </div>
    </AppLayout>
  );
}
