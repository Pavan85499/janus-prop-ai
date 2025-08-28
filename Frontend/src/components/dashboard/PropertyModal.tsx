import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { 
  MapPin, 
  DollarSign, 
  TrendingUp, 
  Home, 
  Calendar,
  Users,
  Briefcase,
  Star,
  ExternalLink,
  Calculator
} from "lucide-react";

interface PropertyModalProps {
  property: any;
  open: boolean;
  onClose: () => void;
}

export function PropertyModal({ property, open, onClose }: PropertyModalProps) {
  if (!property) return null;

  const getScoreColor = (score: number) => {
    if (score >= 85) return "text-success bg-success/10 border-success/20";
    if (score >= 70) return "text-warning bg-warning/10 border-warning/20"; 
    return "text-destructive bg-destructive/10 border-destructive/20";
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto bg-card/95 backdrop-blur-sm border-border/50">
        <DialogHeader>
          <DialogTitle className="font-display text-2xl font-normal">
            Property Intelligence Report
          </DialogTitle>
        </DialogHeader>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Main Info */}
          <div className="lg:col-span-2 space-y-6">
            {/* Property Header */}
            <div className="space-y-4">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-display text-xl font-normal">{property.address}</h3>
                  <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <DollarSign className="w-4 h-4" />
                      {property.price}
                    </span>
                    <span className="flex items-center gap-1">
                      <Home className="w-4 h-4" />
                      {property.rentEstimate} rent
                    </span>
                  </div>
                </div>
                
                <Badge className={`${getScoreColor(property.lienScore)} font-mono text-lg px-3 py-1`}>
                  {property.lienScore}
                </Badge>
              </div>

              {/* AI Summary */}
              <Card className="bg-primary/5 border-primary/20">
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Star className="w-5 h-5 text-primary" />
                    Janus AI Analysis
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm leading-relaxed">{property.aiSummary}</p>
                </CardContent>
              </Card>
            </div>

            {/* Financial Analysis */}
            <Card className="data-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calculator className="w-5 h-5" />
                  Financial Projections
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Purchase Price</span>
                      <span className="font-mono">{property.price}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Monthly Rent</span>
                      <span className="font-mono text-success">{property.rentEstimate}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Cap Rate</span>
                      <span className="font-mono text-success font-medium">{property.capRate}%</span>
                    </div>
                  </div>
                  
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Cash Flow (Monthly)</span>
                      <span className="font-mono text-success">+$1,247</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">ROI (Annual)</span>
                      <span className="font-mono text-success">18.3%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Break-even</span>
                      <span className="font-mono">2.1 years</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Investment Strategy */}
            <Card className="data-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5" />
                  Recommended Strategy
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <Badge className="bg-primary/20 text-primary border-primary/30 text-base px-4 py-2">
                    {property.strategy}
                  </Badge>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-3 bg-secondary/20 rounded-lg">
                      <div className="text-sm text-muted-foreground">Timeline</div>
                      <div className="font-medium">3-5 years</div>
                    </div>
                    <div className="p-3 bg-secondary/20 rounded-lg">
                      <div className="text-sm text-muted-foreground">Risk Level</div>
                      <div className="font-medium capitalize">{property.risk}</div>
                    </div>
                    <div className="p-3 bg-secondary/20 rounded-lg">
                      <div className="text-sm text-muted-foreground">Confidence</div>
                      <div className="font-medium">94%</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Actions & Details */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <Card className="data-card">
              <CardHeader>
                <CardTitle>Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button className="w-full bg-gradient-primary glow-primary">
                  <Briefcase className="w-4 h-4 mr-2" />
                  Add to Portfolio
                </Button>
                
                <Button variant="outline" className="w-full">
                  <Star className="w-4 h-4 mr-2" />
                  Save to Watchlist
                </Button>
                
                <Button variant="outline" className="w-full">
                  <ExternalLink className="w-4 h-4 mr-2" />
                  View on Map
                </Button>
              </CardContent>
            </Card>

            {/* Property Details */}
            <Card className="data-card">
              <CardHeader>
                <CardTitle>Property Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Property Type</span>
                    <span>Single Family</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Year Built</span>
                    <span>1995</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Square Feet</span>
                    <span>1,847 sq ft</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Bedrooms</span>
                    <span>3 bed</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Bathrooms</span>
                    <span>2 bath</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Lot Size</span>
                    <span>0.21 acres</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Lien Information */}
            <Card className="data-card">
              <CardHeader>
                <CardTitle>Lien Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Lien Amount</span>
                    <span className="text-warning font-medium">$12,847</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Interest Rate</span>
                    <span>8% annually</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Redemption Period</span>
                    <span>180 days</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Market Discount</span>
                    <span className="text-success font-medium">35%</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        <Separator className="my-6" />

        <div className="flex justify-between items-center">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Calendar className="w-4 h-4" />
            Last updated: 3 minutes ago
          </div>
          
          <div className="flex gap-3">
            <Button variant="outline" onClick={onClose}>
              Close
            </Button>
            <Button className="bg-gradient-primary glow-primary">
              Schedule Analysis
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}