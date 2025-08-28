import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Map, List, Star, Eye, MoreHorizontal } from "lucide-react";
import { motion } from "framer-motion";

const mockProperties = [
  {
    id: 1,
    address: "123 Oak Street, Brooklyn, NY 11201",
    price: 485000,
    estimatedValue: 620000,
    equity: 22,
    type: "Single Family",
    beds: 3,
    baths: 2,
    sqft: 1200,
    janusScore: 94,
    distressLevel: "High",
    image: "/placeholder.svg"
  },
  {
    id: 2,
    address: "456 Maple Ave, Queens, NY 11355",
    price: 325000,
    estimatedValue: 415000,
    equity: 28,
    type: "Multi Family",
    beds: 4,
    baths: 3,
    sqft: 1800,
    janusScore: 87,
    distressLevel: "Medium",
    image: "/placeholder.svg"
  },
  {
    id: 3,
    address: "789 Pine Road, Bronx, NY 10451",
    price: 195000,
    estimatedValue: 280000,
    equity: 30,
    type: "Townhouse",
    beds: 2,
    baths: 1,
    sqft: 950,
    janusScore: 91,
    distressLevel: "High",
    image: "/placeholder.svg"
  }
];

interface MapListViewProps {
  onPropertySelect: (property: any) => void;
  onPropertyDetail: (property: any) => void;
}

export function MapListView({ onPropertySelect, onPropertyDetail }: MapListViewProps) {
  const [viewMode, setViewMode] = useState<'map' | 'list'>('list');

  const getScoreColor = (score: number) => {
    if (score >= 90) return "bg-gold text-gold-foreground";
    if (score >= 80) return "bg-ice text-ice-foreground";
    return "bg-muted text-muted-foreground";
  };

  const getDistressColor = (level: string) => {
    switch (level) {
      case "High": return "bg-destructive/20 text-destructive border-destructive/30";
      case "Medium": return "bg-warning/20 text-warning border-warning/30";
      default: return "bg-success/20 text-success border-success/30";
    }
  };

  return (
    <div className="flex-1 flex flex-col bg-background">
      {/* View Toggle Header */}
      <div className="p-6 border-b border-border bg-card">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="font-display text-xl font-semibold text-foreground mb-1">
              Investment Opportunities
            </h2>
            <p className="text-sm text-muted-foreground">
              {mockProperties.length} properties match your criteria
            </p>
          </div>
          <div className="flex items-center gap-2 bg-muted rounded-lg p-1">
            <Button
              variant={viewMode === 'map' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('map')}
              className={viewMode === 'map' ? 'bg-ice text-ice-foreground' : 'hover:bg-background/50'}
            >
              <Map className="w-4 h-4 mr-2" />
              Map
            </Button>
            <Button
              variant={viewMode === 'list' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('list')}
              className={viewMode === 'list' ? 'bg-ice text-ice-foreground' : 'hover:bg-background/50'}
            >
              <List className="w-4 h-4 mr-2" />
              List
            </Button>
          </div>
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 p-6">
        {viewMode === 'map' ? (
          // Map View
          <div className="h-full bg-muted rounded-lg border border-border flex items-center justify-center">
            <div className="text-center">
              <Map className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="font-display text-lg font-semibold text-foreground mb-2">
                Interactive Property Map
              </h3>
              <p className="text-sm text-muted-foreground max-w-md">
                Dynamic real estate map with color-coded opportunity scoring. 
                Click pins to preview properties and see AI insights.
              </p>
            </div>
          </div>
        ) : (
          // List View
          <div className="space-y-4 h-full overflow-y-auto">
            {mockProperties.map((property, index) => (
              <motion.div
                key={property.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
              >
                <Card 
                  className="bg-card border-border hover:border-ice/50 transition-all duration-200 cursor-pointer"
                  onClick={() => onPropertySelect(property)}
                >
                  <CardContent className="p-6">
                    <div className="flex gap-6">
                      {/* Property Image */}
                      <div className="w-32 h-24 bg-muted rounded-lg shrink-0 overflow-hidden">
                        <img 
                          src={property.image} 
                          alt={property.address}
                          className="w-full h-full object-cover"
                        />
                      </div>

                      {/* Property Details */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between mb-3">
                          <div>
                            <h3 className="font-medium text-foreground mb-1 truncate">
                              {property.address}
                            </h3>
                            <div className="flex items-center gap-4 text-sm text-muted-foreground">
                              <span>{property.beds} bed</span>
                              <span>{property.baths} bath</span>
                              <span>{property.sqft.toLocaleString()} sqft</span>
                              <span>{property.type}</span>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <Badge className={getScoreColor(property.janusScore)}>
                              Score: {property.janusScore}
                            </Badge>
                            <Badge 
                              variant="outline" 
                              className={getDistressColor(property.distressLevel)}
                            >
                              {property.distressLevel} Distress
                            </Badge>
                          </div>
                        </div>

                        <div className="grid grid-cols-4 gap-4 mb-4">
                          <div>
                            <p className="text-xs text-muted-foreground mb-1">List Price</p>
                            <p className="font-semibold text-foreground">
                              ${property.price.toLocaleString()}
                            </p>
                          </div>
                          <div>
                            <p className="text-xs text-muted-foreground mb-1">Est. Value</p>
                            <p className="font-semibold text-ice">
                              ${property.estimatedValue.toLocaleString()}
                            </p>
                          </div>
                          <div>
                            <p className="text-xs text-muted-foreground mb-1">Equity</p>
                            <p className="font-semibold text-gold">
                              {property.equity}%
                            </p>
                          </div>
                          <div>
                            <p className="text-xs text-muted-foreground mb-1">Potential Gain</p>
                            <p className="font-semibold text-success">
                              ${(property.estimatedValue - property.price).toLocaleString()}
                            </p>
                          </div>
                        </div>

                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-4">
                            <Button 
                              size="sm" 
                              variant="outline" 
                              className="border-border hover:bg-muted"
                              onClick={(e) => {
                                e.stopPropagation();
                                onPropertyDetail(property);
                              }}
                            >
                              <Eye className="w-4 h-4 mr-2" />
                              View Details
                            </Button>
                            <Button size="sm" variant="ghost" className="hover:bg-muted">
                              <Star className="w-4 h-4 mr-2" />
                              Save
                            </Button>
                          </div>
                          <Button size="sm" variant="ghost" className="hover:bg-muted">
                            <MoreHorizontal className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}