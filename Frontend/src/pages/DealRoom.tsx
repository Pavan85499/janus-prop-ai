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
  Handshake, 
  DollarSign, 
  TrendingUp,
  Search,
  Filter,
  RefreshCw,
  Eye,
  Edit,
  Trash2,
  Clock,
  Users,
  FileText,
  MessageSquare,
  Calendar,
  MapPin,
  Building2,
  Target,
  AlertCircle,
  CheckCircle,
  XCircle
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { AppLayout } from "@/components/layout/AppLayout";

interface Deal {
  id: string;
  title: string;
  description: string;
  propertyAddress: string;
  propertyType: string;
  dealType: 'acquisition' | 'disposition' | 'refinance' | 'partnership' | 'development';
  status: 'prospecting' | 'under_review' | 'due_diligence' | 'negotiation' | 'under_contract' | 'closed' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  askingPrice: number;
  offerPrice?: number;
  estimatedValue: number;
  capRate: number;
  roi: number;
  dealSize: number;
  expectedCloseDate: string;
  actualCloseDate?: string;
  buyer?: string;
  seller?: string;
  agent?: string;
  broker?: string;
  lender?: string;
  inspector?: string;
  attorney?: string;
  documents: string[];
  notes: string[];
  tasks: DealTask[];
  created_at: string;
  updated_at: string;
  lastActivity: string;
}

interface DealTask {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled';
  assignedTo: string;
  dueDate: string;
  completedDate?: string;
  priority: 'low' | 'medium' | 'high';
}

const DEAL_TYPES = [
  { value: "acquisition", label: "Acquisition", description: "Purchasing a property" },
  { value: "disposition", label: "Disposition", description: "Selling a property" },
  { value: "refinance", label: "Refinance", description: "Refinancing existing property" },
  { value: "partnership", label: "Partnership", description: "Joint venture or partnership deal" },
  { value: "development", label: "Development", description: "New development project" },
];

const DEAL_STATUS = [
  "prospecting",
  "under_review", 
  "due_diligence",
  "negotiation",
  "under_contract",
  "closed",
  "cancelled"
];

const PRIORITY_LEVELS = [
  { value: "low", label: "Low", color: "bg-muted/20 text-muted-foreground border-muted/30" },
  { value: "medium", label: "Medium", color: "bg-warning/20 text-warning border-warning/30" },
  { value: "high", label: "High", color: "bg-destructive/20 text-destructive border-destructive/30" },
  { value: "urgent", label: "Urgent", color: "bg-destructive/20 text-destructive border-destructive/30" },
];

export default function DealRoom() {
  const { toast } = useToast();
  
  const [deals, setDeals] = useState<Deal[]>([]);
  const [loading, setLoading] = useState(false);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [selectedDeal, setSelectedDeal] = useState<Deal | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [typeFilter, setTypeFilter] = useState<string>("all");
  const [priorityFilter, setPriorityFilter] = useState<string>("all");
  
  const [newDeal, setNewDeal] = useState({
    title: "",
    description: "",
    propertyAddress: "",
    propertyType: "",
    dealType: "",
    priority: "",
    askingPrice: 0,
    estimatedValue: 0,
    expectedCloseDate: "",
    buyer: "",
    seller: "",
  });

  // Load deals
  useEffect(() => {
    loadDeals();
  }, []);

  const loadDeals = async () => {
    try {
      setLoading(true);
      // Mock data for now
      const mockDeals: Deal[] = [
        {
          id: "1",
          title: "Austin Office Building Acquisition",
          description: "Prime downtown office building with excellent tenant mix",
          propertyAddress: "123 Congress Ave, Austin, TX 78701",
          propertyType: "Commercial",
          dealType: "acquisition",
          status: "due_diligence",
          priority: "high",
          askingPrice: 2500000,
          offerPrice: 2350000,
          estimatedValue: 2400000,
          capRate: 6.8,
          roi: 12.5,
          dealSize: 2500000,
          expectedCloseDate: "2024-12-15",
          buyer: "Janus Investment Group",
          seller: "Austin Properties LLC",
          agent: "Sarah Johnson",
          broker: "CBRE",
          lender: "Wells Fargo",
          inspector: "Austin Inspections",
          attorney: "Smith & Associates",
          documents: ["Purchase Agreement", "Financial Statements", "Property Inspection"],
          notes: ["Due diligence period extended by 5 days", "Lender approval pending"],
          tasks: [
            {
              id: "1",
              title: "Property Inspection",
              description: "Complete comprehensive property inspection",
              status: "completed",
              assignedTo: "Austin Inspections",
              dueDate: "2024-11-20",
              completedDate: "2024-11-18",
              priority: "high"
            },
            {
              id: "2",
              title: "Financial Review",
              description: "Review tenant leases and financial statements",
              status: "in_progress",
              assignedTo: "Sarah Johnson",
              dueDate: "2024-11-25",
              priority: "high"
            }
          ],
          created_at: "2024-10-15T00:00:00Z",
          updated_at: new Date().toISOString(),
          lastActivity: new Date().toISOString(),
        },
        {
          id: "2",
          title: "Houston Multi-Family Disposition",
          description: "24-unit apartment complex in growing Houston suburb",
          propertyAddress: "456 Main Street, Houston, TX 77001",
          propertyType: "Multi-Family",
          dealType: "disposition",
          status: "negotiation",
          priority: "medium",
          askingPrice: 3200000,
          offerPrice: 3100000,
          estimatedValue: 3150000,
          capRate: 7.2,
          roi: 15.8,
          dealSize: 3200000,
          expectedCloseDate: "2024-12-30",
          buyer: "Houston Capital Partners",
          seller: "Janus Investment Group",
          agent: "Mike Chen",
          broker: "Marcus & Millichap",
          lender: "Chase Bank",
          documents: ["Listing Agreement", "Property Disclosures", "Financial Records"],
          notes: ["Buyer requesting 60-day closing", "Price negotiation ongoing"],
          tasks: [
            {
              id: "3",
              title: "Market Analysis",
              description: "Complete comparative market analysis",
              status: "completed",
              assignedTo: "Mike Chen",
              dueDate: "2024-11-15",
              completedDate: "2024-11-14",
              priority: "medium"
            },
            {
              id: "4",
              title: "Buyer Qualification",
              description: "Verify buyer financial capacity",
              status: "pending",
              assignedTo: "Marcus & Millichap",
              dueDate: "2024-11-30",
              priority: "high"
            }
          ],
          created_at: "2024-09-20T00:00:00Z",
          updated_at: new Date().toISOString(),
          lastActivity: new Date().toISOString(),
        },
        {
          id: "3",
          title: "Dallas Development Partnership",
          description: "Mixed-use development project in downtown Dallas",
          propertyAddress: "789 Commerce Street, Dallas, TX 75201",
          propertyType: "Mixed-Use",
          dealType: "partnership",
          status: "under_contract",
          priority: "urgent",
          askingPrice: 15000000,
          offerPrice: 14500000,
          estimatedValue: 14800000,
          capRate: 5.5,
          roi: 18.2,
          dealSize: 15000000,
          expectedCloseDate: "2024-12-10",
          buyer: "Dallas Development Partners",
          seller: "City of Dallas",
          agent: "Jennifer Lee",
          broker: "JLL",
          lender: "Bank of America",
          documents: ["Partnership Agreement", "Development Plans", "Zoning Approvals"],
          notes: ["Final zoning approval received", "Construction loan approved"],
          tasks: [
            {
              id: "5",
              title: "Zoning Approval",
              description: "Obtain final zoning approval for development",
              status: "completed",
              assignedTo: "Jennifer Lee",
              dueDate: "2024-11-10",
              completedDate: "2024-11-08",
              priority: "urgent"
            },
            {
              id: "6",
              title: "Construction Loan",
              description: "Finalize construction loan documentation",
              status: "completed",
              assignedTo: "Bank of America",
              dueDate: "2024-11-15",
              completedDate: "2024-11-12",
              priority: "urgent"
            }
          ],
          created_at: "2024-08-10T00:00:00Z",
          updated_at: new Date().toISOString(),
          lastActivity: new Date().toISOString(),
        }
      ];
      setDeals(mockDeals);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load deals",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const createDeal = async () => {
    try {
      setLoading(true);
      const deal: Deal = {
        id: Date.now().toString(),
        ...newDeal,
        status: "prospecting",
        capRate: 0,
        roi: 0,
        dealSize: newDeal.askingPrice,
        documents: [],
        notes: [],
        tasks: [],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        lastActivity: new Date().toISOString(),
      };

      setDeals(prev => [deal, ...prev]);
      setShowCreateDialog(false);
      setNewDeal({
        title: "",
        description: "",
        propertyAddress: "",
        propertyType: "",
        dealType: "",
        priority: "",
        askingPrice: 0,
        estimatedValue: 0,
        expectedCloseDate: "",
        buyer: "",
        seller: "",
      });

      toast({
        title: "Success",
        description: "Deal created successfully",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create deal",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'prospecting': return 'bg-muted/20 text-muted-foreground border-muted/30';
      case 'under_review': return 'bg-info/20 text-info border-info/30';
      case 'due_diligence': return 'bg-warning/20 text-warning border-warning/30';
      case 'negotiation': return 'bg-primary/20 text-primary border-primary/30';
      case 'under_contract': return 'bg-success/20 text-success border-success/30';
      case 'closed': return 'bg-success/20 text-success border-success/30';
      case 'cancelled': return 'bg-destructive/20 text-destructive border-destructive/30';
      default: return 'bg-muted/20 text-muted-foreground border-muted/30';
    }
  };

  const getPriorityColor = (priority: string) => {
    const priorityLevel = PRIORITY_LEVELS.find(p => p.value === priority);
    return priorityLevel?.color || 'bg-muted/20 text-muted-foreground border-muted/30';
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'prospecting': return <Target className="w-4 h-4" />;
      case 'under_review': return <Eye className="w-4 h-4" />;
      case 'due_diligence': return <FileText className="w-4 h-4" />;
      case 'negotiation': return <Handshake className="w-4 h-4" />;
      case 'under_contract': return <CheckCircle className="w-4 h-4" />;
      case 'closed': return <CheckCircle className="w-4 h-4" />;
      case 'cancelled': return <XCircle className="w-4 h-4" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  const filteredDeals = deals.filter(deal => {
    const matchesSearch = deal.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         deal.propertyAddress.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         deal.buyer?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         deal.seller?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === "all" || deal.status === statusFilter;
    const matchesType = typeFilter === "all" || deal.dealType === typeFilter;
    const matchesPriority = priorityFilter === "all" || deal.priority === priorityFilter;
    return matchesSearch && matchesStatus && matchesType && matchesPriority;
  });

  const totalDealValue = deals.reduce((sum, d) => sum + d.dealSize, 0);
  const activeDeals = deals.filter(d => !['closed', 'cancelled'].includes(d.status)).length;
  const closedDeals = deals.filter(d => d.status === 'closed').length;
  const avgROI = deals.length > 0 ? deals.reduce((sum, d) => sum + d.roi, 0) / deals.length : 0;

  return (
    <AppLayout>
      <div className="min-h-screen bg-gradient-to-br from-background to-muted">
      {/* Header */}
      <div className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold">Deal Room</h1>
              <p className="text-muted-foreground mt-1">
                Manage your real estate transactions and deals
              </p>
            </div>
            <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
              <DialogTrigger asChild>
                <Button className="flex items-center gap-2">
                  <Plus className="w-4 h-4" />
                  New Deal
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-2xl">
                <DialogHeader>
                  <DialogTitle>Create New Deal</DialogTitle>
                  <DialogDescription>
                    Add a new real estate transaction to your deal room
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="title">Deal Title</Label>
                    <Input
                      id="title"
                      value={newDeal.title}
                      onChange={(e) => setNewDeal(prev => ({ ...prev, title: e.target.value }))}
                      placeholder="Enter deal title"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="description">Description</Label>
                    <Textarea
                      id="description"
                      value={newDeal.description}
                      onChange={(e) => setNewDeal(prev => ({ ...prev, description: e.target.value }))}
                      placeholder="Describe the deal..."
                      rows={3}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="propertyAddress">Property Address</Label>
                    <Input
                      id="propertyAddress"
                      value={newDeal.propertyAddress}
                      onChange={(e) => setNewDeal(prev => ({ ...prev, propertyAddress: e.target.value }))}
                      placeholder="123 Main Street, City, State ZIP"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="dealType">Deal Type</Label>
                      <Select value={newDeal.dealType} onValueChange={(value) => setNewDeal(prev => ({ ...prev, dealType: value }))}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select deal type" />
                        </SelectTrigger>
                        <SelectContent>
                          {DEAL_TYPES.map((type) => (
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
                    <div className="space-y-2">
                      <Label htmlFor="priority">Priority</Label>
                      <Select value={newDeal.priority} onValueChange={(value) => setNewDeal(prev => ({ ...prev, priority: value }))}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select priority" />
                        </SelectTrigger>
                        <SelectContent>
                          {PRIORITY_LEVELS.map((priority) => (
                            <SelectItem key={priority.value} value={priority.value}>
                              {priority.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="askingPrice">Asking Price</Label>
                      <Input
                        id="askingPrice"
                        type="number"
                        value={newDeal.askingPrice}
                        onChange={(e) => setNewDeal(prev => ({ ...prev, askingPrice: Number(e.target.value) }))}
                        placeholder="2500000"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="estimatedValue">Estimated Value</Label>
                      <Input
                        id="estimatedValue"
                        type="number"
                        value={newDeal.estimatedValue}
                        onChange={(e) => setNewDeal(prev => ({ ...prev, estimatedValue: Number(e.target.value) }))}
                        placeholder="2400000"
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="buyer">Buyer</Label>
                      <Input
                        id="buyer"
                        value={newDeal.buyer}
                        onChange={(e) => setNewDeal(prev => ({ ...prev, buyer: e.target.value }))}
                        placeholder="Buyer name or company"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="seller">Seller</Label>
                      <Input
                        id="seller"
                        value={newDeal.seller}
                        onChange={(e) => setNewDeal(prev => ({ ...prev, seller: e.target.value }))}
                        placeholder="Seller name or company"
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="expectedCloseDate">Expected Close Date</Label>
                    <Input
                      id="expectedCloseDate"
                      type="date"
                      value={newDeal.expectedCloseDate}
                      onChange={(e) => setNewDeal(prev => ({ ...prev, expectedCloseDate: e.target.value }))}
                    />
                  </div>
                  <div className="flex justify-end space-x-2">
                    <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                      Cancel
                    </Button>
                    <Button onClick={createDeal} disabled={loading}>
                      {loading ? "Creating..." : "Create Deal"}
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
                <Handshake className="w-5 h-5 text-primary" />
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Deals</p>
                  <p className="text-2xl font-bold">{deals.length}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <TrendingUp className="w-5 h-5 text-success" />
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Active Deals</p>
                  <p className="text-2xl font-bold">{activeDeals}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <DollarSign className="w-5 h-5 text-warning" />
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Value</p>
                  <p className="text-2xl font-bold">${(totalDealValue / 1000000).toFixed(1)}M</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5 text-info" />
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Closed Deals</p>
                  <p className="text-2xl font-bold">{closedDeals}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Filters */}
        <div className="flex items-center space-x-4 mb-6">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
              <Input
                placeholder="Search deals..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="Filter by status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              {DEAL_STATUS.map((status) => (
                <SelectItem key={status} value={status}>
                  {status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={typeFilter} onValueChange={setTypeFilter}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="Filter by type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
              {DEAL_TYPES.map((type) => (
                <SelectItem key={type.value} value={type.value}>
                  {type.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={priorityFilter} onValueChange={setPriorityFilter}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="Filter by priority" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Priorities</SelectItem>
              {PRIORITY_LEVELS.map((priority) => (
                <SelectItem key={priority.value} value={priority.value}>
                  {priority.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button variant="outline" onClick={loadDeals}>
            <RefreshCw className="w-4 h-4" />
          </Button>
        </div>

        {/* Deals Table */}
        <Card>
          <CardHeader>
            <CardTitle>Deals</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                <p className="mt-2 text-muted-foreground">Loading deals...</p>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Deal</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Priority</TableHead>
                    <TableHead>Value</TableHead>
                    <TableHead>ROI</TableHead>
                    <TableHead>Close Date</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredDeals.map((deal) => (
                    <TableRow key={deal.id}>
                      <TableCell>
                        <div className="flex items-center space-x-2">
                          {getStatusIcon(deal.status)}
                          <div>
                            <div className="font-medium">{deal.title}</div>
                            <div className="text-sm text-muted-foreground flex items-center space-x-1">
                              <MapPin className="w-3 h-3" />
                              <span>{deal.propertyAddress}</span>
                            </div>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">
                          {DEAL_TYPES.find(t => t.value === deal.dealType)?.label}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Badge className={getStatusColor(deal.status)}>
                          {deal.status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Badge className={getPriorityColor(deal.priority)}>
                          {deal.priority}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div>
                          <div className="font-medium">${(deal.dealSize / 1000000).toFixed(1)}M</div>
                          {deal.offerPrice && (
                            <div className="text-sm text-muted-foreground">
                              Offer: ${(deal.offerPrice / 1000000).toFixed(1)}M
                            </div>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="font-medium">{deal.roi}%</div>
                        <div className="text-sm text-muted-foreground">
                          Cap: {deal.capRate}%
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center space-x-1">
                          <Calendar className="w-3 h-3 text-muted-foreground" />
                          <span className="text-sm">
                            {new Date(deal.expectedCloseDate).toLocaleDateString()}
                          </span>
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
                          <Button size="sm" variant="outline">
                            <MessageSquare className="w-3 h-3" />
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
