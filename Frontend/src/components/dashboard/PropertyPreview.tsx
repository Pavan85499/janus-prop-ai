import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { 
  MapPin, 
  Calendar, 
  Home, 
  DollarSign, 
  TrendingUp, 
  Eye, 
  Star, 
  Phone,
  FileText,
  Bot
} from "lucide-react";

interface PropertyPreviewProps {
  property?: any;
}

export function PropertyPreview({ property }: PropertyPreviewProps) {
  if (!property) {
    return (
      <div className="w-96 h-screen bg-card border-l border-border p-6 flex items-center justify-center">
        <div className="text-center">
          <Home className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="font-display text-lg font-semibold text-foreground mb-2">
            Select a Property
          </h3>
          <p className="text-sm text-muted-foreground">
            Click on a property from the map or list to see AI-powered insights and detailed analysis.
          </p>
        </div>
      </div>
    );
  }

  const getScoreColor = (score: number) => {
    if (score >= 90) return "bg-gold text-gold-foreground";
    if (score >= 80) return "bg-ice text-ice-foreground";
    return "bg-muted text-muted-foreground";
  };

  const equityGain = property.estimatedValue - property.price;
  const equityPercentage = ((equityGain / property.price) * 100).toFixed(1);

  return (
    <div className="w-96 h-screen bg-card border-l border-border overflow-y-auto">
      {/* Property Header */}
      <div className="p-6 border-b border-border">
        <div className="mb-4">
          <img 
            src={property.image || "/placeholder.svg"} 
            alt={property.address}
            className="w-full h-48 bg-muted rounded-lg object-cover"
          />
        </div>
        
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1 min-w-0">
            <h3 className="font-display text-lg font-semibold text-foreground mb-2">
              {property.address}
            </h3>
            <div className="flex items-center gap-2 text-sm text-muted-foreground mb-3">
              <MapPin className="w-4 h-4" />
              <span>Brooklyn, NY 11201</span>
            </div>
          </div>
          <Badge className={getScoreColor(property.janusScore)}>
            Janus Score: {property.janusScore}
          </Badge>
        </div>

        <div className="grid grid-cols-3 gap-3 mb-4">
          <div className="text-center">
            <p className="text-xs text-muted-foreground mb-1">Beds</p>
            <p className="font-semibold text-foreground">{property.beds}</p>
          </div>
          <div className="text-center">
            <p className="text-xs text-muted-foreground mb-1">Baths</p>
            <p className="font-semibold text-foreground">{property.baths}</p>
          </div>
          <div className="text-center">
            <p className="text-xs text-muted-foreground mb-1">Sqft</p>
            <p className="font-semibold text-foreground">{property.sqft.toLocaleString()}</p>
          </div>
        </div>
      </div>

      {/* Financial Stats */}
      <div className="p-6 border-b border-border">
        <h4 className="font-display text-base font-semibold text-foreground mb-4">
          Financial Overview
        </h4>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">List Price</span>
            <span className="font-semibold text-foreground">
              ${property.price.toLocaleString()}
            </span>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Est. Market Value</span>
            <span className="font-semibold text-ice">
              ${property.estimatedValue.toLocaleString()}
            </span>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Potential Equity</span>
            <span className="font-semibold text-gold">
              ${equityGain.toLocaleString()} ({equityPercentage}%)
            </span>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Property Type</span>
            <span className="font-medium text-foreground">{property.type}</span>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Owner Type</span>
            <span className="font-medium text-foreground">Absentee</span>
          </div>
        </div>
      </div>

      {/* AI Insight */}
      <div className="p-6 border-b border-border">
        <div className="flex items-center gap-2 mb-4">
          <Bot className="w-5 h-5 text-ice" />
          <h4 className="font-display text-base font-semibold text-foreground">
            Janus AI Insight
          </h4>
        </div>
        
        <Card className="bg-secondary border-border">
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 bg-ice/20 rounded-full flex items-center justify-center shrink-0">
                <Bot className="w-4 h-4 text-ice" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-ice mb-1">Eden & Orion Analysis</p>
                <p className="text-sm text-foreground leading-relaxed italic break-words">
                  "Eden: This {property.type.toLowerCase()} ranks in our top 15% of opportunities based on multi-agent analysis. 
                  Orion identified it through foreclosure monitoring, while Osiris projects {equityPercentage}% upside. 
                  Atelius confirms clean legal status. Our coordinated analysis suggests immediate action for this high-value target."
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <div className="p-6 border-b border-border">
        <h4 className="font-display text-base font-semibold text-foreground mb-4">
          Quick Actions
        </h4>
        
        <div className="space-y-3">
          <Button className="w-full justify-start bg-ice text-ice-foreground hover:bg-ice/90">
            <Eye className="w-4 h-4 mr-2" />
            View Full Details
          </Button>
          
          <Button variant="outline" className="w-full justify-start border-border hover:bg-muted">
            <Star className="w-4 h-4 mr-2" />
            Save to Watchlist
          </Button>
          
          <Button variant="outline" className="w-full justify-start border-border hover:bg-muted">
            <MapPin className="w-4 h-4 mr-2" />
            View on Map
          </Button>
        </div>
      </div>

      {/* Property Details */}
      <div className="p-6 border-b border-border">
        <h4 className="font-display text-base font-semibold text-foreground mb-4">
          Property Details
        </h4>
        
        <div className="space-y-3 text-sm">
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground">Year Built</span>
            <span className="text-foreground">1985</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground">Lot Size</span>
            <span className="text-foreground">0.15 acres</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground">Tax Assessment</span>
            <span className="text-foreground">$420,000</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground">Days on Market</span>
            <span className="text-foreground">273 days</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground">Last Sale</span>
            <span className="text-foreground">$380K (2019)</span>
          </div>
        </div>
      </div>

      {/* Next Steps */}
      <div className="p-6">
        <h4 className="font-display text-base font-semibold text-foreground mb-4">
          Recommended Next Steps
        </h4>
        
        <div className="space-y-2">
          <Button variant="ghost" size="sm" className="w-full justify-start hover:bg-muted text-left">
            <Phone className="w-4 h-4 mr-2 text-ice" />
            <div>
              <p className="font-medium">Contact Owner (Valyria)</p>
              <p className="text-xs text-muted-foreground">Pre-filled outreach template</p>
            </div>
          </Button>
          
          <Button variant="ghost" size="sm" className="w-full justify-start hover:bg-muted text-left">
            <TrendingUp className="w-4 h-4 mr-2 text-gold" />
            <div>
              <p className="font-medium">Run Rehab Estimator (Osiris)</p>
              <p className="text-xs text-muted-foreground">AI cost analysis</p>
            </div>
          </Button>
          
          <Button variant="ghost" size="sm" className="w-full justify-start hover:bg-muted text-left">
            <FileText className="w-4 h-4 mr-2 text-success" />
            <div>
              <p className="font-medium">Draft Offer Letter (Celestia)</p>
              <p className="text-xs text-muted-foreground">AI-generated template</p>
            </div>
          </Button>

          <Button variant="ghost" size="sm" className="w-full justify-start hover:bg-muted text-left">
            <Bot className="w-4 h-4 mr-2 text-warning" />
            <div>
              <p className="font-medium">Legal Review (Atelius)</p>
              <p className="text-xs text-muted-foreground">Title and lien analysis</p>
            </div>
          </Button>
        </div>
      </div>
    </div>
  );
}