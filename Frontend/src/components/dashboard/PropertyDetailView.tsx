import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { 
  ChevronLeft, 
  ChevronRight, 
  ChevronDown,
  Bot, 
  Phone, 
  Mail, 
  FileText, 
  Calculator,
  Plus,
  Eye,
  MapPin,
  Calendar,
  DollarSign,
  TrendingUp,
  Home,
  Clock,
  User,
  Building,
  Gavel,
  BarChart3,
  Brain,
  Search,
  Shield,
  GitBranch,
  Database,
  CheckCircle
} from "lucide-react";
import { motion } from "framer-motion";

interface PropertyDetailViewProps {
  property?: any;
  open: boolean;
  onClose: () => void;
}

const agentIcons = {
  "Celestia": FileText,
  "Valyria": Phone,
  "Eden": Brain,
  "Osiris": Calculator,
  "Orion": Search,
  "Atelius": Shield,
  "Aurora": GitBranch,
  "Elysia": Database,
  "Spring": CheckCircle
};

const mockPropertyImages = [
  "/placeholder.svg",
  "/placeholder.svg", 
  "/placeholder.svg",
  "/placeholder.svg"
];

const mockOwnershipHistory = [
  { owner: "John Smith", purchaseDate: "2019-03-15", price: 380000, saleDate: null },
  { owner: "Sarah Johnson", purchaseDate: "2015-08-22", price: 320000, saleDate: "2019-03-15" },
  { owner: "Mike Davis", purchaseDate: "2012-01-10", price: 285000, saleDate: "2015-08-22" }
];

const mockComparables = [
  { address: "125 Oak Street", beds: 3, baths: 2, sqft: 1250, price: 535000, date: "2024-01-10", distance: "0.1 mi" },
  { address: "119 Oak Street", beds: 2, baths: 2, sqft: 1100, price: 485000, date: "2023-12-15", distance: "0.1 mi" },
  { address: "130 Maple Ave", beds: 3, baths: 2, sqft: 1300, price: 575000, date: "2023-11-20", distance: "0.2 mi" }
];

const recommendedAgents = [
  { name: "Celestia", role: "Report Generator", task: "Generate comprehensive investment memo", icon: FileText },
  { name: "Valyria", role: "Market Forecaster", task: "Analyze neighborhood market trends", icon: Phone },
  { name: "Eden", role: "Executive Strategist", task: "Recommend optimal acquisition strategy", icon: Brain },
  { name: "Osiris", role: "Financial Modeler", task: "Create detailed cash flow projections", icon: Calculator },
  { name: "Atelius", role: "Legal Intelligence", task: "Complete legal due diligence review", icon: Shield }
];

export function PropertyDetailView({ property, open, onClose }: PropertyDetailViewProps) {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [nextActionsExpanded, setNextActionsExpanded] = useState(false);

  if (!property) return null;

  const equityGain = property.estimatedValue - property.price;
  const equityPercentage = ((equityGain / property.price) * 100).toFixed(1);

  const nextImage = () => {
    setCurrentImageIndex((prev) => (prev + 1) % mockPropertyImages.length);
  };

  const prevImage = () => {
    setCurrentImageIndex((prev) => (prev - 1 + mockPropertyImages.length) % mockPropertyImages.length);
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-6xl h-[90vh] bg-card border-border p-0">
        <div className="flex h-full">
          {/* Main Content Area */}
          <div className="flex-1 flex flex-col">
            {/* Header */}
            <DialogHeader className="p-6 border-b border-border">
              <DialogTitle className="font-display text-2xl font-semibold text-foreground">
                {property.address}
              </DialogTitle>
              <div className="flex items-center gap-4 mt-2">
                <Badge className="bg-gold text-gold-foreground">
                  Janus Score: {property.janusScore}
                </Badge>
                <Badge variant="outline" className="border-ice text-ice">
                  High Opportunity
                </Badge>
                <span className="text-sm text-muted-foreground">
                  Listed {property.daysOnMarket || 273} days ago
                </span>
              </div>
            </DialogHeader>

            {/* Photo Carousel */}
            <div className="relative h-64 bg-muted border-b border-border">
              <img 
                src={mockPropertyImages[currentImageIndex]} 
                alt={`Property view ${currentImageIndex + 1}`}
                className="w-full h-full object-cover"
              />
              <Button
                variant="ghost"
                size="icon"
                className="absolute left-4 top-1/2 -translate-y-1/2 bg-background/80 hover:bg-background/90"
                onClick={prevImage}
              >
                <ChevronLeft className="w-5 h-5" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="absolute right-4 top-1/2 -translate-y-1/2 bg-background/80 hover:bg-background/90"
                onClick={nextImage}
              >
                <ChevronRight className="w-5 h-5" />
              </Button>
              <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2">
                {mockPropertyImages.map((_, index) => (
                  <button
                    key={index}
                    className={`w-2 h-2 rounded-full transition-colors ${
                      index === currentImageIndex ? 'bg-ice' : 'bg-background/60'
                    }`}
                    onClick={() => setCurrentImageIndex(index)}
                  />
                ))}
              </div>
            </div>

            {/* Detailed Data Tabs */}
            <div className="flex-1 p-6">
              <Tabs defaultValue="overview" className="h-full">
                <TabsList className="grid w-full grid-cols-5 bg-muted">
                  <TabsTrigger value="overview" className="data-[state=active]:bg-ice data-[state=active]:text-ice-foreground">
                    Overview
                  </TabsTrigger>
                  <TabsTrigger value="ownership" className="data-[state=active]:bg-ice data-[state=active]:text-ice-foreground">
                    Ownership
                  </TabsTrigger>
                  <TabsTrigger value="financial" className="data-[state=active]:bg-ice data-[state=active]:text-ice-foreground">
                    Financial
                  </TabsTrigger>
                  <TabsTrigger value="comparables" className="data-[state=active]:bg-ice data-[state=active]:text-ice-foreground">
                    Comparables
                  </TabsTrigger>
                  <TabsTrigger value="legal" className="data-[state=active]:bg-ice data-[state=active]:text-ice-foreground">
                    Legal
                  </TabsTrigger>
                </TabsList>

                <ScrollArea className="h-[400px] mt-4">
                  <TabsContent value="overview" className="space-y-4">
                    <div className="grid grid-cols-2 gap-6">
                      <Card className="bg-secondary border-border">
                        <CardHeader>
                          <CardTitle className="text-base">Property Details</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-3">
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Type</span>
                            <span className="font-medium">{property.type}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Year Built</span>
                            <span className="font-medium">1985</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Lot Size</span>
                            <span className="font-medium">0.15 acres</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Bedrooms</span>
                            <span className="font-medium">{property.beds}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Bathrooms</span>
                            <span className="font-medium">{property.baths}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Square Feet</span>
                            <span className="font-medium">{property.sqft?.toLocaleString()}</span>
                          </div>
                        </CardContent>
                      </Card>

                      <Card className="bg-secondary border-border">
                        <CardHeader>
                          <CardTitle className="text-base">Financial Summary</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-3">
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">List Price</span>
                            <span className="font-medium">${property.price?.toLocaleString()}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Est. Market Value</span>
                            <span className="font-medium text-ice">${property.estimatedValue?.toLocaleString()}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Potential Equity</span>
                            <span className="font-medium text-gold">${equityGain?.toLocaleString()}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Tax Assessment</span>
                            <span className="font-medium">$420,000</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Monthly Taxes</span>
                            <span className="font-medium">$1,250</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Est. Rent</span>
                            <span className="font-medium text-success">$2,800/mo</span>
                          </div>
                        </CardContent>
                      </Card>
                    </div>
                  </TabsContent>

                  <TabsContent value="ownership" className="space-y-4">
                    <Card className="bg-secondary border-border">
                      <CardHeader>
                        <CardTitle className="text-base">Ownership History</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-4">
                          {mockOwnershipHistory.map((record, index) => (
                            <div key={index} className="flex items-center justify-between p-3 bg-muted rounded-lg">
                              <div>
                                <p className="font-medium text-foreground">{record.owner}</p>
                                <p className="text-sm text-muted-foreground">
                                  {record.purchaseDate} - {record.saleDate || "Present"}
                                </p>
                              </div>
                              <div className="text-right">
                                <p className="font-medium text-foreground">${record.price.toLocaleString()}</p>
                                <p className="text-sm text-muted-foreground">Purchase Price</p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  </TabsContent>

                  <TabsContent value="financial" className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <Card className="bg-secondary border-border">
                        <CardHeader>
                          <CardTitle className="text-base">Cash Flow Analysis</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-3">
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Monthly Rent</span>
                            <span className="font-medium text-success">$2,800</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Property Taxes</span>
                            <span className="font-medium text-destructive">-$1,250</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Insurance</span>
                            <span className="font-medium text-destructive">-$180</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Maintenance</span>
                            <span className="font-medium text-destructive">-$280</span>
                          </div>
                          <Separator />
                          <div className="flex justify-between font-semibold">
                            <span>Net Cash Flow</span>
                            <span className="text-success">$1,090/mo</span>
                          </div>
                        </CardContent>
                      </Card>

                      <Card className="bg-secondary border-border">
                        <CardHeader>
                          <CardTitle className="text-base">Investment Metrics</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-3">
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Cap Rate</span>
                            <span className="font-medium text-ice">6.9%</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Cash on Cash</span>
                            <span className="font-medium text-gold">11.2%</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">1% Rule</span>
                            <span className="font-medium text-success">✓ Pass</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">50% Rule</span>
                            <span className="font-medium text-success">✓ Pass</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">DSCR</span>
                            <span className="font-medium text-ice">1.35</span>
                          </div>
                        </CardContent>
                      </Card>
                    </div>
                  </TabsContent>

                  <TabsContent value="comparables" className="space-y-4">
                    <Card className="bg-secondary border-border">
                      <CardHeader>
                        <CardTitle className="text-base">Recent Comparable Sales</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          {mockComparables.map((comp, index) => (
                            <div key={index} className="flex items-center justify-between p-3 bg-muted rounded-lg">
                              <div>
                                <p className="font-medium text-foreground">{comp.address}</p>
                                <p className="text-sm text-muted-foreground">
                                  {comp.beds} bed, {comp.baths} bath • {comp.sqft.toLocaleString()} sqft • {comp.distance}
                                </p>
                              </div>
                              <div className="text-right">
                                <p className="font-medium text-foreground">${comp.price.toLocaleString()}</p>
                                <p className="text-sm text-muted-foreground">{comp.date}</p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  </TabsContent>

                  <TabsContent value="legal" className="space-y-4">
                    <Card className="bg-secondary border-border">
                      <CardHeader>
                        <CardTitle className="text-base">Legal & Compliance</CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                          <div className="flex items-center gap-3">
                            <CheckCircle className="w-5 h-5 text-success" />
                            <span className="font-medium">Clean Title</span>
                          </div>
                          <Badge variant="outline" className="border-success text-success">Verified</Badge>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                          <div className="flex items-center gap-3">
                            <CheckCircle className="w-5 h-5 text-success" />
                            <span className="font-medium">No Outstanding Liens</span>
                          </div>
                          <Badge variant="outline" className="border-success text-success">Clear</Badge>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                          <div className="flex items-center gap-3">
                            <Gavel className="w-5 h-5 text-warning" />
                            <span className="font-medium">Code Violations</span>
                          </div>
                          <Badge variant="outline" className="border-warning text-warning">2 Minor</Badge>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                          <div className="flex items-center gap-3">
                            <Building className="w-5 h-5 text-ice" />
                            <span className="font-medium">Zoning</span>
                          </div>
                          <span className="font-medium">R-6 Residential</span>
                        </div>
                      </CardContent>
                    </Card>
                  </TabsContent>
                </ScrollArea>
              </Tabs>
            </div>
          </div>

          {/* Right Sidebar - AI Insights & Actions */}
          <div className="w-96 border-l border-border bg-secondary">
            <ScrollArea className="h-full">
              <div className="p-6 space-y-6">
                {/* Janus Insight Panel */}
                <Card className="bg-card border-border">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-base">
                      <Bot className="w-5 h-5 text-ice" />
                      Janus AI Analysis
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="p-4 bg-ice/10 border border-ice/20 rounded-lg">
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 bg-ice/20 rounded-full flex items-center justify-center shrink-0">
                          <Search className="w-4 h-4 text-ice" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-ice mb-1">Multi-Agent Analysis</p>
                          <p className="text-sm text-foreground leading-relaxed italic break-words">
                            "Eden: Final ranking places this in top 8% of all opportunities. Orion identified through foreclosure monitoring. 
                            Osiris projects {equityPercentage}% equity gain with 18-month timeline. Atelius confirms clean title. 
                            Valyria forecasts 15% neighborhood appreciation. Spring validated all data points. 
                            Aurora coordinated this comprehensive analysis. Elysia enriched with comparable sales data. 
                            This represents a rare combination of high return potential with verified low risk."
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div className="text-center p-3 bg-muted rounded-lg">
                        <p className="text-lg font-bold text-gold">{equityPercentage}%</p>
                        <p className="text-xs text-muted-foreground">Below Market</p>
                      </div>
                      <div className="text-center p-3 bg-muted rounded-lg">
                        <p className="text-lg font-bold text-ice">6.9%</p>
                        <p className="text-xs text-muted-foreground">Cap Rate</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Next Actions Panel */}
                <Card className="bg-card border-border">
                  <Collapsible open={nextActionsExpanded} onOpenChange={setNextActionsExpanded}>
                    <CollapsibleTrigger asChild>
                      <CardHeader className="cursor-pointer hover:bg-muted/30 transition-colors">
                        <CardTitle className="flex items-center justify-between text-base">
                          <span>Next Steps</span>
                          <ChevronDown className={`w-4 h-4 transition-transform ${nextActionsExpanded ? 'rotate-180' : ''}`} />
                        </CardTitle>
                      </CardHeader>
                    </CollapsibleTrigger>
                    <CollapsibleContent>
                      <CardContent className="space-y-3">
                        <Button className="w-full justify-start bg-ice text-ice-foreground hover:bg-ice/90">
                          <Phone className="w-4 h-4 mr-2" />
                          Contact Owner (Valyria)
                        </Button>
                        <Button variant="outline" className="w-full justify-start border-border hover:bg-muted">
                          <Plus className="w-4 h-4 mr-2" />
                          Add to Leads (Aurora)
                        </Button>
                        <Button variant="outline" className="w-full justify-start border-border hover:bg-muted">
                          <Calculator className="w-4 h-4 mr-2" />
                          Rehab Estimator (Osiris)
                        </Button>
                        <Button variant="outline" className="w-full justify-start border-border hover:bg-muted">
                          <FileText className="w-4 h-4 mr-2" />
                          Draft Offer (Celestia)
                        </Button>
                        <Button variant="outline" className="w-full justify-start border-border hover:bg-muted">
                          <Shield className="w-4 h-4 mr-2" />
                          Legal Review (Atelius)
                        </Button>
                      </CardContent>
                    </CollapsibleContent>
                  </Collapsible>
                </Card>

                {/* Agent Suggestions Panel */}
                <Card className="bg-card border-border">
                  <CardHeader>
                    <CardTitle className="text-base">Recommended Agents</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {recommendedAgents.map((agent, index) => {
                      const IconComponent = agent.icon;
                      return (
                        <div key={index} className="p-3 bg-muted rounded-lg hover:bg-muted/70 transition-colors cursor-pointer">
                          <div className="flex items-start gap-3">
                            <div className="w-8 h-8 bg-ice/20 rounded-full flex items-center justify-center shrink-0">
                              <IconComponent className="w-4 h-4 text-ice" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className="font-medium text-foreground text-sm">{agent.name}</p>
                              <p className="text-xs text-muted-foreground mb-1">{agent.role}</p>
                              <p className="text-xs text-foreground">{agent.task}</p>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </CardContent>
                </Card>

                {/* Quick Actions */}
                <div className="space-y-3">
                  <Button variant="outline" className="w-full border-border hover:bg-muted">
                    <Eye className="w-4 h-4 mr-2" />
                    Schedule Viewing
                  </Button>
                  <Button variant="outline" className="w-full border-border hover:bg-muted">
                    <MapPin className="w-4 h-4 mr-2" />
                    View Neighborhood
                  </Button>
                  <Button variant="outline" className="w-full border-border hover:bg-muted">
                    <BarChart3 className="w-4 h-4 mr-2" />
                    Market Analysis
                  </Button>
                </div>
              </div>
            </ScrollArea>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}