import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Switch } from '@/components/ui/switch';
import { 
  Search, 
  Filter, 
  MapPin, 
  DollarSign, 
  Home, 
  TrendingUp, 
  AlertTriangle,
  CheckCircle,
  Clock,
  Play,
  Pause,
  Square,
  Download,
  Eye,
  BarChart3,
  Target,
  Zap
} from 'lucide-react';
import { AppLayout } from '@/components/layout/AppLayout';

const PropertyScanner = () => {
  const [activeTab, setActiveTab] = useState('create');
  const [scans, setScans] = useState([]);
  const [currentScan, setCurrentScan] = useState(null);
  const [scanProgress, setScanProgress] = useState(0);
  const [isScanning, setIsScanning] = useState(false);
  const [scanResults, setScanResults] = useState([]);
  
  // Scan creation form
  const [scanForm, setScanForm] = useState({
    name: '',
    description: '',
    maxProperties: 10000,
    radiusMiles: 50,
    // Location
    city: '',
    state: '',
    zipCodes: '',
    // Property filters
    propertyTypes: [],
    minPrice: '',
    maxPrice: '',
    minSqft: '',
    maxSqft: '',
    minBedrooms: '',
    maxBedrooms: '',
    minBathrooms: '',
    maxBathrooms: '',
    // Investment criteria
    minROI: '',
    maxROI: '',
    minCapRate: '',
    maxCapRate: '',
    // Distress indicators
    includeDistressed: true,
    includeForeclosures: true,
    includeShortSales: true,
    includeBankOwned: true,
    minDaysOnMarket: '',
    maxDaysOnMarket: '',
    maxPriceReductions: ''
  });

  const [filters, setFilters] = useState({
    investmentPotential: '',
    isDistressed: '',
    isUndervalued: '',
    minROI: '',
    maxROI: '',
    minConfidence: ''
  });

  // Mock data for demonstration
  const mockScans = [
    {
      id: 1,
      name: 'San Francisco Distressed Properties',
      description: 'Scanning for distressed properties in SF Bay Area',
      status: 'completed',
      created_at: '2024-01-15T10:30:00Z',
      completed_at: '2024-01-15T11:45:00Z',
      total_scanned: 5000,
      properties_found: 127,
      high_potential_count: 23,
      distressed_count: 45,
      undervalued_count: 67
    },
    {
      id: 2,
      name: 'Oakland Commercial Properties',
      description: 'Commercial real estate opportunities in Oakland',
      status: 'running',
      created_at: '2024-01-16T09:15:00Z',
      total_scanned: 2500,
      properties_found: 89,
      high_potential_count: 12,
      distressed_count: 23,
      undervalued_count: 34
    },
    {
      id: 3,
      name: 'Silicon Valley High ROI',
      description: 'High ROI residential properties in Silicon Valley',
      status: 'pending',
      created_at: '2024-01-16T14:20:00Z',
      total_scanned: 0,
      properties_found: 0,
      high_potential_count: 0,
      distressed_count: 0,
      undervalued_count: 0
    }
  ];

  const mockResults = [
    {
      id: 1,
      address: '123 Main St, San Francisco, CA 94102',
      city: 'San Francisco',
      state: 'CA',
      property_type: 'residential',
      bedrooms: 3,
      bathrooms: 2.5,
      square_feet: 1800,
      list_price: 1200000,
      estimated_value: 1140000,
      price_per_sqft: 667,
      investment_potential: 'high',
      roi_estimate: 12.5,
      cap_rate: 7.2,
      is_distressed: false,
      is_undervalued: true,
      is_foreclosure: false,
      ai_confidence_score: 0.89,
      ai_analysis: 'Property shows strong investment potential with 12.5% ROI. Market analysis indicates undervalued by 5%.',
      scanned_at: '2024-01-15T11:30:00Z'
    },
    {
      id: 2,
      address: '456 Oak Ave, Oakland, CA 94601',
      city: 'Oakland',
      state: 'CA',
      property_type: 'residential',
      bedrooms: 4,
      bathrooms: 3,
      square_feet: 2200,
      list_price: 850000,
      estimated_value: 900000,
      price_per_sqft: 386,
      investment_potential: 'very_high',
      roi_estimate: 15.8,
      cap_rate: 8.5,
      is_distressed: true,
      is_undervalued: true,
      is_foreclosure: true,
      ai_confidence_score: 0.92,
      ai_analysis: 'Excellent distressed property opportunity. Foreclosure with 15.8% ROI potential. Strong appreciation outlook.',
      scanned_at: '2024-01-15T11:32:00Z'
    },
    {
      id: 3,
      address: '789 Commercial Blvd, San Jose, CA 95110',
      city: 'San Jose',
      state: 'CA',
      property_type: 'commercial',
      bedrooms: 0,
      bathrooms: 2,
      square_feet: 5000,
      list_price: 2500000,
      estimated_value: 2400000,
      price_per_sqft: 500,
      investment_potential: 'medium',
      roi_estimate: 8.2,
      cap_rate: 5.8,
      is_distressed: false,
      is_undervalued: false,
      is_foreclosure: false,
      ai_confidence_score: 0.76,
      ai_analysis: 'Stable commercial property with moderate investment potential. Good for long-term hold strategy.',
      scanned_at: '2024-01-15T11:35:00Z'
    }
  ];

  useEffect(() => {
    setScans(mockScans);
    setScanResults(mockResults);
  }, []);

  const handleCreateScan = () => {
    // In production, this would call the API
    const newScan = {
      id: Date.now(),
      name: scanForm.name,
      description: scanForm.description,
      status: 'running',
      created_at: new Date().toISOString(),
      total_scanned: 0,
      properties_found: 0,
      high_potential_count: 0,
      distressed_count: 0,
      undervalued_count: 0
    };
    
    setScans([newScan, ...scans]);
    setIsScanning(true);
    setCurrentScan(newScan);
    
    // Simulate scanning progress
    let progress = 0;
    const interval = setInterval(() => {
      progress += Math.random() * 10;
      if (progress >= 100) {
        progress = 100;
        setIsScanning(false);
        clearInterval(interval);
        setScans(prev => prev.map(scan => 
          scan.id === newScan.id 
            ? { ...scan, status: 'completed', completed_at: new Date().toISOString() }
            : scan
        ));
      }
      setScanProgress(progress);
    }, 1000);
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      pending: { variant: 'secondary', icon: Clock },
      running: { variant: 'default', icon: Play },
      completed: { variant: 'default', icon: CheckCircle },
      failed: { variant: 'destructive', icon: AlertTriangle },
      cancelled: { variant: 'outline', icon: Square }
    };
    
    const config = statusConfig[status] || statusConfig.pending;
    const Icon = config.icon;
    
    return (
      <Badge variant={config.variant} className="flex items-center gap-1">
        <Icon className="h-3 w-3" />
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  const getInvestmentBadge = (potential: string) => {
    const config = {
      very_high: { variant: 'default', color: 'text-green-600' },
      high: { variant: 'default', color: 'text-green-500' },
      medium: { variant: 'secondary', color: 'text-yellow-600' },
      low: { variant: 'outline', color: 'text-red-600' }
    };
    
    const { variant, color } = config[potential] || config.medium;
    
    return (
      <Badge variant={variant} className={color}>
        {potential.replace('_', ' ').toUpperCase()}
      </Badge>
    );
  };

  return (
    <AppLayout>
      <div className="flex-1 space-y-6 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Property Scanner</h2>
          <p className="text-muted-foreground">
            Scan millions of properties for distressed, undervalued, or high-potential assets
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline">
            <Download className="mr-2 h-4 w-4" />
            Export Results
          </Button>
          <Button onClick={() => setActiveTab('create')}>
            <Search className="mr-2 h-4 w-4" />
            New Scan
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList>
          <TabsTrigger value="create">Create Scan</TabsTrigger>
          <TabsTrigger value="scans">Active Scans</TabsTrigger>
          <TabsTrigger value="results">Scan Results</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="create" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5" />
                Create Property Scan
              </CardTitle>
              <CardDescription>
                Configure your property search criteria and start scanning for investment opportunities
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Basic Information */}
              <div className="space-y-4">
                <h4 className="text-lg font-medium">Basic Information</h4>
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <Label htmlFor="scan-name">Scan Name</Label>
                    <Input
                      id="scan-name"
                      value={scanForm.name}
                      onChange={(e) => setScanForm({...scanForm, name: e.target.value})}
                      placeholder="e.g., San Francisco Distressed Properties"
                    />
                  </div>
                  <div>
                    <Label htmlFor="max-properties">Max Properties</Label>
                    <Input
                      id="max-properties"
                      type="number"
                      value={scanForm.maxProperties}
                      onChange={(e) => setScanForm({...scanForm, maxProperties: parseInt(e.target.value)})}
                    />
                  </div>
                </div>
                <div>
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    value={scanForm.description}
                    onChange={(e) => setScanForm({...scanForm, description: e.target.value})}
                    placeholder="Describe your scanning criteria and objectives"
                    rows={3}
                  />
                </div>
              </div>

              {/* Location Filters */}
              <div className="space-y-4">
                <h4 className="text-lg font-medium flex items-center gap-2">
                  <MapPin className="h-5 w-5" />
                  Location Filters
                </h4>
                <div className="grid gap-4 md:grid-cols-3">
                  <div>
                    <Label htmlFor="city">City</Label>
                    <Input
                      id="city"
                      value={scanForm.city}
                      onChange={(e) => setScanForm({...scanForm, city: e.target.value})}
                      placeholder="San Francisco"
                    />
                  </div>
                  <div>
                    <Label htmlFor="state">State</Label>
                    <Input
                      id="state"
                      value={scanForm.state}
                      onChange={(e) => setScanForm({...scanForm, state: e.target.value})}
                      placeholder="CA"
                    />
                  </div>
                  <div>
                    <Label htmlFor="zip-codes">ZIP Codes</Label>
                    <Input
                      id="zip-codes"
                      value={scanForm.zipCodes}
                      onChange={(e) => setScanForm({...scanForm, zipCodes: e.target.value})}
                      placeholder="94102, 94103, 94104"
                    />
                  </div>
                </div>
                <div>
                  <Label htmlFor="radius">Search Radius (miles)</Label>
                  <Input
                    id="radius"
                    type="number"
                    value={scanForm.radiusMiles}
                    onChange={(e) => setScanForm({...scanForm, radiusMiles: parseFloat(e.target.value)})}
                  />
                </div>
              </div>

              {/* Property Filters */}
              <div className="space-y-4">
                <h4 className="text-lg font-medium flex items-center gap-2">
                  <Home className="h-5 w-5" />
                  Property Filters
                </h4>
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <Label htmlFor="property-types">Property Types</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select property types" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="residential">Residential</SelectItem>
                        <SelectItem value="commercial">Commercial</SelectItem>
                        <SelectItem value="industrial">Industrial</SelectItem>
                        <SelectItem value="mixed-use">Mixed Use</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <Label htmlFor="min-price">Min Price</Label>
                      <Input
                        id="min-price"
                        type="number"
                        value={scanForm.minPrice}
                        onChange={(e) => setScanForm({...scanForm, minPrice: e.target.value})}
                        placeholder="$500,000"
                      />
                    </div>
                    <div>
                      <Label htmlFor="max-price">Max Price</Label>
                      <Input
                        id="max-price"
                        type="number"
                        value={scanForm.maxPrice}
                        onChange={(e) => setScanForm({...scanForm, maxPrice: e.target.value})}
                        placeholder="$2,000,000"
                      />
                    </div>
                  </div>
                </div>
                <div className="grid gap-4 md:grid-cols-3">
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <Label htmlFor="min-sqft">Min Sq Ft</Label>
                      <Input
                        id="min-sqft"
                        type="number"
                        value={scanForm.minSqft}
                        onChange={(e) => setScanForm({...scanForm, minSqft: e.target.value})}
                      />
                    </div>
                    <div>
                      <Label htmlFor="max-sqft">Max Sq Ft</Label>
                      <Input
                        id="max-sqft"
                        type="number"
                        value={scanForm.maxSqft}
                        onChange={(e) => setScanForm({...scanForm, maxSqft: e.target.value})}
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <Label htmlFor="min-bedrooms">Min Bedrooms</Label>
                      <Input
                        id="min-bedrooms"
                        type="number"
                        value={scanForm.minBedrooms}
                        onChange={(e) => setScanForm({...scanForm, minBedrooms: e.target.value})}
                      />
                    </div>
                    <div>
                      <Label htmlFor="max-bedrooms">Max Bedrooms</Label>
                      <Input
                        id="max-bedrooms"
                        type="number"
                        value={scanForm.maxBedrooms}
                        onChange={(e) => setScanForm({...scanForm, maxBedrooms: e.target.value})}
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <Label htmlFor="min-bathrooms">Min Bathrooms</Label>
                      <Input
                        id="min-bathrooms"
                        type="number"
                        value={scanForm.minBathrooms}
                        onChange={(e) => setScanForm({...scanForm, minBathrooms: e.target.value})}
                      />
                    </div>
                    <div>
                      <Label htmlFor="max-bathrooms">Max Bathrooms</Label>
                      <Input
                        id="max-bathrooms"
                        type="number"
                        value={scanForm.maxBathrooms}
                        onChange={(e) => setScanForm({...scanForm, maxBathrooms: e.target.value})}
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Investment Criteria */}
              <div className="space-y-4">
                <h4 className="text-lg font-medium flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  Investment Criteria
                </h4>
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <Label htmlFor="min-roi">Min ROI (%)</Label>
                      <Input
                        id="min-roi"
                        type="number"
                        value={scanForm.minROI}
                        onChange={(e) => setScanForm({...scanForm, minROI: e.target.value})}
                        placeholder="8.0"
                      />
                    </div>
                    <div>
                      <Label htmlFor="max-roi">Max ROI (%)</Label>
                      <Input
                        id="max-roi"
                        type="number"
                        value={scanForm.maxROI}
                        onChange={(e) => setScanForm({...scanForm, maxROI: e.target.value})}
                        placeholder="25.0"
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <Label htmlFor="min-cap-rate">Min Cap Rate (%)</Label>
                      <Input
                        id="min-cap-rate"
                        type="number"
                        value={scanForm.minCapRate}
                        onChange={(e) => setScanForm({...scanForm, minCapRate: e.target.value})}
                        placeholder="5.0"
                      />
                    </div>
                    <div>
                      <Label htmlFor="max-cap-rate">Max Cap Rate (%)</Label>
                      <Input
                        id="max-cap-rate"
                        type="number"
                        value={scanForm.maxCapRate}
                        onChange={(e) => setScanForm({...scanForm, maxCapRate: e.target.value})}
                        placeholder="15.0"
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Distress Indicators */}
              <div className="space-y-4">
                <h4 className="text-lg font-medium flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5" />
                  Distress Indicators
                </h4>
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <Label htmlFor="include-distressed">Include Distressed Properties</Label>
                      <Switch
                        id="include-distressed"
                        checked={scanForm.includeDistressed}
                        onCheckedChange={(checked) => setScanForm({...scanForm, includeDistressed: checked})}
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <Label htmlFor="include-foreclosures">Include Foreclosures</Label>
                      <Switch
                        id="include-foreclosures"
                        checked={scanForm.includeForeclosures}
                        onCheckedChange={(checked) => setScanForm({...scanForm, includeForeclosures: checked})}
                      />
                    </div>
                  </div>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <Label htmlFor="include-short-sales">Include Short Sales</Label>
                      <Switch
                        id="include-short-sales"
                        checked={scanForm.includeShortSales}
                        onCheckedChange={(checked) => setScanForm({...scanForm, includeShortSales: checked})}
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <Label htmlFor="include-bank-owned">Include Bank Owned</Label>
                      <Switch
                        id="include-bank-owned"
                        checked={scanForm.includeBankOwned}
                        onCheckedChange={(checked) => setScanForm({...scanForm, includeBankOwned: checked})}
                      />
                    </div>
                  </div>
                </div>
                <div className="grid gap-4 md:grid-cols-3">
                  <div>
                    <Label htmlFor="min-days-market">Min Days on Market</Label>
                    <Input
                      id="min-days-market"
                      type="number"
                      value={scanForm.minDaysOnMarket}
                      onChange={(e) => setScanForm({...scanForm, minDaysOnMarket: e.target.value})}
                      placeholder="30"
                    />
                  </div>
                  <div>
                    <Label htmlFor="max-days-market">Max Days on Market</Label>
                    <Input
                      id="max-days-market"
                      type="number"
                      value={scanForm.maxDaysOnMarket}
                      onChange={(e) => setScanForm({...scanForm, maxDaysOnMarket: e.target.value})}
                      placeholder="365"
                    />
                  </div>
                  <div>
                    <Label htmlFor="max-price-reductions">Max Price Reductions</Label>
                    <Input
                      id="max-price-reductions"
                      type="number"
                      value={scanForm.maxPriceReductions}
                      onChange={(e) => setScanForm({...scanForm, maxPriceReductions: e.target.value})}
                      placeholder="5"
                    />
                  </div>
                </div>
              </div>

              <div className="flex justify-end space-x-2">
                <Button variant="outline">Save as Template</Button>
                <Button onClick={handleCreateScan} disabled={!scanForm.name}>
                  <Zap className="mr-2 h-4 w-4" />
                  Start Scan
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="scans" className="space-y-4">
          <div className="grid gap-4">
            {scans.map((scan) => (
              <Card key={scan.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        {scan.name}
                        {getStatusBadge(scan.status)}
                      </CardTitle>
                      <CardDescription>{scan.description}</CardDescription>
                    </div>
                    <div className="flex items-center space-x-2">
                      {scan.status === 'running' && (
                        <Button variant="outline" size="sm">
                          <Pause className="h-4 w-4 mr-1" />
                          Pause
                        </Button>
                      )}
                      <Button variant="outline" size="sm">
                        <Eye className="h-4 w-4 mr-1" />
                        View
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid gap-4 md:grid-cols-5">
                    <div className="text-center">
                      <p className="text-2xl font-bold">{scan.total_scanned.toLocaleString()}</p>
                      <p className="text-sm text-muted-foreground">Scanned</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-green-600">{scan.properties_found}</p>
                      <p className="text-sm text-muted-foreground">Found</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-blue-600">{scan.high_potential_count}</p>
                      <p className="text-sm text-muted-foreground">High Potential</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-orange-600">{scan.distressed_count}</p>
                      <p className="text-sm text-muted-foreground">Distressed</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-purple-600">{scan.undervalued_count}</p>
                      <p className="text-sm text-muted-foreground">Undervalued</p>
                    </div>
                  </div>
                  {scan.status === 'running' && (
                    <div className="mt-4">
                      <div className="flex justify-between text-sm mb-2">
                        <span>Scan Progress</span>
                        <span>{Math.round(scanProgress)}%</span>
                      </div>
                      <Progress value={scanProgress} className="h-2" />
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="results" className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Select value={filters.investmentPotential} onValueChange={(value) => setFilters({...filters, investmentPotential: value})}>
                <SelectTrigger className="w-[200px]">
                  <SelectValue placeholder="Investment Potential" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Levels</SelectItem>
                  <SelectItem value="very_high">Very High</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="low">Low</SelectItem>
                </SelectContent>
              </Select>
              <Select value={filters.isDistressed} onValueChange={(value) => setFilters({...filters, isDistressed: value})}>
                <SelectTrigger className="w-[150px]">
                  <SelectValue placeholder="Distressed" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All</SelectItem>
                  <SelectItem value="true">Yes</SelectItem>
                  <SelectItem value="false">No</SelectItem>
                </SelectContent>
              </Select>
              <Button variant="outline">
                <Filter className="h-4 w-4 mr-2" />
                More Filters
              </Button>
            </div>
            <div className="text-sm text-muted-foreground">
              {scanResults.length} properties found
            </div>
          </div>

          <div className="grid gap-4">
            {scanResults.map((property) => (
              <Card key={property.id}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-lg">{property.address}</CardTitle>
                      <CardDescription>
                        {property.city}, {property.state} • {property.property_type.charAt(0).toUpperCase() + property.property_type.slice(1)}
                      </CardDescription>
                    </div>
                    <div className="flex items-center space-x-2">
                      {getInvestmentBadge(property.investment_potential)}
                      {property.is_distressed && (
                        <Badge variant="destructive">Distressed</Badge>
                      )}
                      {property.is_undervalued && (
                        <Badge variant="outline">Undervalued</Badge>
                      )}
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid gap-4 md:grid-cols-4">
                    <div>
                      <h4 className="font-medium mb-2">Property Details</h4>
                      <div className="space-y-1 text-sm">
                        <p>Bedrooms: {property.bedrooms || 'N/A'}</p>
                        <p>Bathrooms: {property.bathrooms || 'N/A'}</p>
                        <p>Sq Ft: {property.square_feet?.toLocaleString() || 'N/A'}</p>
                        <p>Price/SqFt: ${property.price_per_sqft?.toLocaleString() || 'N/A'}</p>
                      </div>
                    </div>
                    <div>
                      <h4 className="font-medium mb-2">Financials</h4>
                      <div className="space-y-1 text-sm">
                        <p>List Price: ${property.list_price?.toLocaleString() || 'N/A'}</p>
                        <p>Est. Value: ${property.estimated_value?.toLocaleString() || 'N/A'}</p>
                        <p>ROI: {property.roi_estimate?.toFixed(1)}%</p>
                        <p>Cap Rate: {property.cap_rate?.toFixed(1)}%</p>
                      </div>
                    </div>
                    <div>
                      <h4 className="font-medium mb-2">AI Analysis</h4>
                      <div className="space-y-1 text-sm">
                        <p>Confidence: {(property.ai_confidence_score * 100)?.toFixed(0)}%</p>
                        <p className="text-muted-foreground line-clamp-2">
                          {property.ai_analysis}
                        </p>
                      </div>
                    </div>
                    <div>
                      <h4 className="font-medium mb-2">Actions</h4>
                      <div className="space-y-2">
                        <Button size="sm" className="w-full">
                          <Eye className="h-4 w-4 mr-1" />
                          View Details
                        </Button>
                        <Button variant="outline" size="sm" className="w-full">
                          <DollarSign className="h-4 w-4 mr-1" />
                          Add to Portfolio
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
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  Scan Performance
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <span className="text-sm">Total Scans</span>
                    <span className="font-medium">{scans.length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Properties Scanned</span>
                    <span className="font-medium">{scans.reduce((sum, scan) => sum + scan.total_scanned, 0).toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Properties Found</span>
                    <span className="font-medium">{scans.reduce((sum, scan) => sum + scan.properties_found, 0)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Success Rate</span>
                    <span className="font-medium text-green-600">
                      {scans.length > 0 ? ((scans.filter(scan => scan.status === 'completed').length / scans.length) * 100).toFixed(1) : 0}%
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  Investment Opportunities
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <span className="text-sm">High Potential</span>
                    <span className="font-medium text-blue-600">
                      {scans.reduce((sum, scan) => sum + scan.high_potential_count, 0)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Distressed</span>
                    <span className="font-medium text-orange-600">
                      {scans.reduce((sum, scan) => sum + scan.distressed_count, 0)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Undervalued</span>
                    <span className="font-medium text-purple-600">
                      {scans.reduce((sum, scan) => sum + scan.undervalued_count, 0)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Avg. ROI</span>
                    <span className="font-medium">
                      {scanResults.length > 0 ? (scanResults.reduce((sum, p) => sum + (p.roi_estimate || 0), 0) / scanResults.length).toFixed(1) : 0}%
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="h-5 w-5" />
                  AI Performance
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <span className="text-sm">Avg. Confidence</span>
                    <span className="font-medium">
                      {scanResults.length > 0 ? ((scanResults.reduce((sum, p) => sum + (p.ai_confidence_score || 0), 0) / scanResults.length) * 100).toFixed(0) : 0}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Analysis Accuracy</span>
                    <span className="font-medium text-green-600">94.2%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Processing Speed</span>
                    <span className="font-medium">2.3s/property</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Data Sources</span>
                    <span className="font-medium">12</span>
                  </div>
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

export default PropertyScanner;
