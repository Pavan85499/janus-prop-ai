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
  Building2, 
  MapPin, 
  DollarSign, 
  TrendingUp,
  Search,
  Filter,
  RefreshCw,
  Eye,
  Edit,
  Trash2,
  Star,
  Calendar,
  Users,
  BarChart3
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { AppLayout } from "@/components/layout/AppLayout";

interface Property {
  id: string;
  address: string;
  city: string;
  state: string;
  zipCode: string;
  propertyType: string;
  status: 'active' | 'pending' | 'sold' | 'off-market';
  price: number;
  estimatedValue: number;
  capRate: number;
  roi: number;
  bedrooms: number;
  bathrooms: number;
  squareFeet: number;
  lotSize: number;
  yearBuilt: number;
  mlsId?: string;
  description: string;
  features: string[];
  images: string[];
  marketTrend: 'rising' | 'stable' | 'declining';
  lastUpdated: string;
  created_at: string;
  updated_at: string;
}

const PROPERTY_TYPES = [
  "Single Family",
  "Multi-Family", 
  "Condo",
  "Townhouse",
  "Commercial",
  "Land",
  "Investment"
];

const PROPERTY_STATUS = [
  "active",
  "pending", 
  "sold",
  "off-market"
];

export default function Properties() {
  const { toast } = useToast();
  
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(false);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [selectedProperty, setSelectedProperty] = useState<Property | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [typeFilter, setTypeFilter] = useState<string>("all");
  
  const [newProperty, setNewProperty] = useState({
    address: "",
    city: "",
    state: "",
    zipCode: "",
    propertyType: "",
    price: 0,
    bedrooms: 0,
    bathrooms: 0,
    squareFeet: 0,
    yearBuilt: 0,
    description: "",
  });

  // Load properties
  useEffect(() => {
    loadProperties();
  }, []);

  const loadProperties = async () => {
    try {
      setLoading(true);
      // Mock data for now - in production, this would fetch from the backend
      const mockProperties: Property[] = [
        {
          id: "1",
          address: "123 Oak Street",
          city: "Austin",
          state: "TX",
          zipCode: "78701",
          propertyType: "Single Family",
          status: "active",
          price: 450000,
          estimatedValue: 475000,
          capRate: 8.5,
          roi: 12.3,
          bedrooms: 3,
          bathrooms: 2,
          squareFeet: 1800,
          lotSize: 0.25,
          yearBuilt: 2015,
          mlsId: "MLS123456",
          description: "Beautiful single-family home in prime Austin location",
          features: ["Hardwood Floors", "Updated Kitchen", "Large Backyard"],
          images: [],
          marketTrend: "rising",
          lastUpdated: new Date().toISOString(),
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        {
          id: "2",
          address: "456 Pine Avenue",
          city: "Houston",
          state: "TX",
          zipCode: "77001",
          propertyType: "Multi-Family",
          status: "pending",
          price: 650000,
          estimatedValue: 680000,
          capRate: 9.2,
          roi: 15.1,
          bedrooms: 6,
          bathrooms: 4,
          squareFeet: 3200,
          lotSize: 0.4,
          yearBuilt: 2010,
          mlsId: "MLS789012",
          description: "Duplex with excellent rental potential",
          features: ["Two Units", "Separate Entrances", "Updated Appliances"],
          images: [],
          marketTrend: "stable",
          lastUpdated: new Date().toISOString(),
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        {
          id: "3",
          address: "789 Maple Drive",
          city: "Dallas",
          state: "TX",
          zipCode: "75201",
          propertyType: "Commercial",
          status: "active",
          price: 1200000,
          estimatedValue: 1250000,
          capRate: 7.8,
          roi: 11.5,
          bedrooms: 0,
          bathrooms: 2,
          squareFeet: 5000,
          lotSize: 0.6,
          yearBuilt: 2005,
          mlsId: "MLS345678",
          description: "Prime commercial property in downtown Dallas",
          features: ["High Traffic Location", "Parking Available", "Modern Buildout"],
          images: [],
          marketTrend: "rising",
          lastUpdated: new Date().toISOString(),
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        }
      ];
      setProperties(mockProperties);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load properties",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const createProperty = async () => {
    try {
      setLoading(true);
      const property: Property = {
        id: Date.now().toString(),
        ...newProperty,
        state: "TX", // Default state
        zipCode: newProperty.zipCode || "00000",
        status: "active",
        estimatedValue: newProperty.price * 1.1, // Mock calculation
        capRate: 8.0, // Mock value
        roi: 10.0, // Mock value
        lotSize: 0.25, // Mock value
        mlsId: `MLS${Date.now()}`,
        features: [],
        images: [],
        marketTrend: "stable",
        lastUpdated: new Date().toISOString(),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      setProperties(prev => [property, ...prev]);
      setShowCreateDialog(false);
      setNewProperty({
        address: "",
        city: "",
        state: "",
        zipCode: "",
        propertyType: "",
        price: 0,
        bedrooms: 0,
        bathrooms: 0,
        squareFeet: 0,
        yearBuilt: 0,
        description: "",
      });

      toast({
        title: "Success",
        description: "Property created successfully",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create property",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-success/20 text-success border-success/30';
      case 'pending': return 'bg-warning/20 text-warning border-warning/30';
      case 'sold': return 'bg-info/20 text-info border-info/30';
      case 'off-market': return 'bg-muted/20 text-muted-foreground border-muted/30';
      default: return 'bg-muted/20 text-muted-foreground border-muted/30';
    }
  };

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'rising': return 'text-success';
      case 'stable': return 'text-warning';
      case 'declining': return 'text-destructive';
      default: return 'text-muted-foreground';
    }
  };

  const filteredProperties = properties.filter(property => {
    const matchesSearch = property.address.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         property.city.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         property.mlsId?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === "all" || property.status === statusFilter;
    const matchesType = typeFilter === "all" || property.propertyType === typeFilter;
    return matchesSearch && matchesStatus && matchesType;
  });

  const totalValue = properties.reduce((sum, p) => sum + p.estimatedValue, 0);
  const activeProperties = properties.filter(p => p.status === 'active').length;
  const avgCapRate = properties.length > 0 ? properties.reduce((sum, p) => sum + p.capRate, 0) / properties.length : 0;

  return (
    <AppLayout>
      <div className="min-h-screen bg-gradient-to-br from-background to-muted">
      {/* Header */}
      <div className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="responsive-container responsive-padding-y">
          <div className="responsive-flex-between">
            <div className="flex-1 min-w-0">
              <h1 className="responsive-heading font-bold">Properties</h1>
              <p className="responsive-body text-muted-foreground mt-1">
                Manage your real estate portfolio
              </p>
            </div>
            <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
              <DialogTrigger asChild>
                <Button className="responsive-flex items-center gap-2 touch-target">
                  <Plus className="w-4 h-4" />
                  <span className="mobile-only">Add</span>
                  <span className="tablet-up">Add Property</span>
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-2xl responsive-container">
                <DialogHeader>
                  <DialogTitle className="responsive-subheading">Add New Property</DialogTitle>
                  <DialogDescription className="responsive-body">
                    Add a new property to your portfolio
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div className="responsive-grid-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="address">Address</Label>
                      <Input
                        id="address"
                        value={newProperty.address}
                        onChange={(e) => setNewProperty(prev => ({ ...prev, address: e.target.value }))}
                        placeholder="123 Main Street"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="city">City</Label>
                      <Input
                        id="city"
                        value={newProperty.city}
                        onChange={(e) => setNewProperty(prev => ({ ...prev, city: e.target.value }))}
                        placeholder="Austin"
                      />
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-3 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="zipCode">ZIP Code</Label>
                      <Input
                        id="zipCode"
                        value={newProperty.zipCode}
                        onChange={(e) => setNewProperty(prev => ({ ...prev, zipCode: e.target.value }))}
                        placeholder="78701"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="propertyType">Type</Label>
                      <Select value={newProperty.propertyType} onValueChange={(value) => setNewProperty(prev => ({ ...prev, propertyType: value }))}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select type" />
                        </SelectTrigger>
                        <SelectContent>
                          {PROPERTY_TYPES.map((type) => (
                            <SelectItem key={type} value={type}>
                              {type}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="price">Price</Label>
                      <Input
                        id="price"
                        type="number"
                        value={newProperty.price}
                        onChange={(e) => setNewProperty(prev => ({ ...prev, price: Number(e.target.value) }))}
                        placeholder="450000"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-4 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="bedrooms">Bedrooms</Label>
                      <Input
                        id="bedrooms"
                        type="number"
                        value={newProperty.bedrooms}
                        onChange={(e) => setNewProperty(prev => ({ ...prev, bedrooms: Number(e.target.value) }))}
                        placeholder="3"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="bathrooms">Bathrooms</Label>
                      <Input
                        id="bathrooms"
                        type="number"
                        value={newProperty.bathrooms}
                        onChange={(e) => setNewProperty(prev => ({ ...prev, bathrooms: Number(e.target.value) }))}
                        placeholder="2"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="squareFeet">Sq Ft</Label>
                      <Input
                        id="squareFeet"
                        type="number"
                        value={newProperty.squareFeet}
                        onChange={(e) => setNewProperty(prev => ({ ...prev, squareFeet: Number(e.target.value) }))}
                        placeholder="1800"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="yearBuilt">Year Built</Label>
                      <Input
                        id="yearBuilt"
                        type="number"
                        value={newProperty.yearBuilt}
                        onChange={(e) => setNewProperty(prev => ({ ...prev, yearBuilt: Number(e.target.value) }))}
                        placeholder="2015"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="description">Description</Label>
                    <Textarea
                      id="description"
                      value={newProperty.description}
                      onChange={(e) => setNewProperty(prev => ({ ...prev, description: e.target.value }))}
                      placeholder="Property description..."
                      rows={3}
                    />
                  </div>

                  <div className="flex justify-end space-x-2">
                    <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                      Cancel
                    </Button>
                    <Button onClick={createProperty} disabled={loading}>
                      {loading ? "Adding..." : "Add Property"}
                    </Button>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </div>
      </div>

      <div className="responsive-container responsive-padding-y">
        {/* Stats Cards */}
        <div className="responsive-grid-4 gap-4 sm:gap-6 mb-6 sm:mb-8">
          <Card>
            <CardContent className="responsive-padding">
              <div className="responsive-flex items-center space-x-2">
                <Building2 className="w-5 h-5 text-primary" />
                <div>
                  <p className="responsive-caption font-medium text-muted-foreground">Total Properties</p>
                  <p className="responsive-subheading font-bold">{properties.length}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="responsive-padding">
              <div className="responsive-flex items-center space-x-2">
                <TrendingUp className="w-5 h-5 text-success" />
                <div>
                  <p className="responsive-caption font-medium text-muted-foreground">Active Properties</p>
                  <p className="responsive-subheading font-bold">{activeProperties}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="responsive-padding">
              <div className="responsive-flex items-center space-x-2">
                <DollarSign className="w-5 h-5 text-warning" />
                <div>
                  <p className="responsive-caption font-medium text-muted-foreground">Total Value</p>
                  <p className="responsive-subheading font-bold">${(totalValue / 1000000).toFixed(1)}M</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="responsive-padding">
              <div className="responsive-flex items-center space-x-2">
                <BarChart3 className="w-5 h-5 text-info" />
                <div>
                  <p className="responsive-caption font-medium text-muted-foreground">Avg Cap Rate</p>
                  <p className="responsive-subheading font-bold">{avgCapRate.toFixed(1)}%</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Filters */}
        <div className="responsive-flex space-x-2 sm:space-x-4 mb-4 sm:mb-6">
          <div className="flex-1 min-w-0">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
              <Input
                placeholder="Search properties..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 touch-target"
              />
            </div>
          </div>
          <div className="responsive-flex gap-2 sm:gap-4">
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full sm:w-48 touch-target">
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                {PROPERTY_STATUS.map((status) => (
                  <SelectItem key={status} value={status}>
                    {status.charAt(0).toUpperCase() + status.slice(1)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={typeFilter} onValueChange={setTypeFilter}>
              <SelectTrigger className="w-full sm:w-48 touch-target">
              <SelectValue placeholder="Filter by type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
              {PROPERTY_TYPES.map((type) => (
                <SelectItem key={type} value={type}>
                  {type}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
            <Button variant="outline" onClick={loadProperties} className="touch-target">
              <RefreshCw className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Properties Table */}
        <Card>
          <CardHeader>
            <CardTitle className="responsive-subheading">Properties</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                <p className="mt-2 responsive-body text-muted-foreground">Loading properties...</p>
              </div>
            ) : (
              <div className="responsive-table-container">
                <Table className="responsive-table">
                  <TableHeader>
                    <TableRow>
                      <TableHead className="tablet-up">Address</TableHead>
                      <TableHead className="tablet-up">Type</TableHead>
                      <TableHead className="tablet-up">Status</TableHead>
                      <TableHead className="tablet-up">Price</TableHead>
                      <TableHead className="tablet-up">Cap Rate</TableHead>
                      <TableHead className="tablet-up">Market Trend</TableHead>
                      <TableHead className="tablet-up">Actions</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredProperties.map((property) => (
                    <TableRow key={property.id}>
                      <TableCell>
                        <div className="flex items-center space-x-2">
                          <MapPin className="w-4 h-4 text-muted-foreground" />
                          <div>
                            <div className="font-medium">{property.address}</div>
                            <div className="text-sm text-muted-foreground">
                              {property.city}, {property.state} {property.zipCode}
                            </div>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">
                          {property.propertyType}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Badge className={getStatusColor(property.status)}>
                          {property.status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div>
                          <div className="font-medium">${property.price.toLocaleString()}</div>
                          <div className="text-sm text-muted-foreground">
                            Est: ${property.estimatedValue.toLocaleString()}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="font-medium">{property.capRate}%</div>
                        <div className="text-sm text-muted-foreground">
                          ROI: {property.roi}%
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className={`flex items-center space-x-1 ${getTrendColor(property.marketTrend)}`}>
                          <TrendingUp className="w-4 h-4" />
                          <span className="capitalize">{property.marketTrend}</span>
                        </div>
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
              </div>
            )}
          </CardContent>
        </Card>
      </div>
      </div>
    </AppLayout>
  );
}
