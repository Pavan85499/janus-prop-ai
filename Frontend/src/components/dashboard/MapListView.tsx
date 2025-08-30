import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Map, List, Star, Eye, MoreHorizontal, RefreshCw, AlertCircle } from "lucide-react";
import { motion } from "framer-motion";
import { useRealEstateAPIs } from "@/hooks/useRealEstateAPIs";

interface MapListViewProps {
  onPropertySelect: (property: any) => void;
  onPropertyDetail: (property: any) => void;
}

export function MapListView({ onPropertySelect, onPropertyDetail }: MapListViewProps) {
  const [viewMode, setViewMode] = useState<'map' | 'list'>('list');
  
  // Use real-time real estate APIs data
  const {
    properties: realEstateProperties,
    summary,
    loading,
    error,
    isConnected,
    lastUpdated,
    refreshProperties,
    testConnection
  } = useRealEstateAPIs(true, 60000); // Auto-refresh every minute

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

  // Convert real estate APIs data format to component format
  const properties = realEstateProperties.map(prop => ({
    id: prop.id,
    address: prop.address,
    price: prop.price || 0,
    estimatedValue: prop.estimated_value || 0,
    equity: prop.estimated_value && prop.price ? ((prop.estimated_value - prop.price) / prop.price * 100) : 0,
    type: prop.property_type,
    beds: prop.beds || 0,
    baths: prop.baths || 0,
    sqft: prop.sqft || 0,
    janusScore: Math.round((prop.api_confidence || 0.8) * 100), // Convert API confidence to score
    distressLevel: prop.market_trend === "Declining" ? "High" : prop.market_trend === "Stable" ? "Medium" : "Low",
    image: "/placeholder.svg"
  }));

  return (
    <div className="flex-1 flex flex-col bg-background">
      {/* View Toggle Header */}
      <div className="p-6 border-b border-border bg-card">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="font-display text-xl font-semibold text-foreground mb-1">
              Investment Opportunities
            </h2>
            <div className="flex items-center gap-4">
              <p className="text-sm text-muted-foreground">
                {properties.length} properties match your criteria
                {lastUpdated && (
                  <span className="ml-2 text-xs text-muted-foreground">
                    • Updated {lastUpdated.toLocaleTimeString()}
                  </span>
                )}
              </p>
              <div className="flex items-center gap-2">
                {!isConnected && (
                  <Badge variant="destructive" className="text-xs">
                    <AlertCircle className="w-3 h-3 mr-1" />
                    Offline
                  </Badge>
                )}
                <Button
                  size="sm"
                  variant="outline"
                  onClick={refreshProperties}
                  disabled={loading}
                  className="h-7 px-2"
                >
                  <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
                </Button>
              </div>
            </div>
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
        {/* Error Display */}
        {error && (
          <div className="mb-6 p-4 bg-destructive/10 border border-destructive/20 rounded-md">
            <div className="flex items-center gap-2 text-destructive">
              <AlertCircle className="h-4 w-4" />
              <span className="font-medium">Error:</span>
            </div>
            <p className="text-sm text-destructive mt-1">{error}</p>
            <Button
              size="sm"
              variant="outline"
              onClick={testConnection}
              className="mt-2"
            >
              Test Connection
            </Button>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center py-12">
            <RefreshCw className="w-8 h-8 animate-spin text-muted-foreground" />
            <span className="ml-3 text-muted-foreground">Loading investment opportunities...</span>
          </div>
        )}

        {/* No Data State */}
        {!loading && properties.length === 0 && (
          <div className="text-center py-12">
            <Map className="w-12 h-12 mx-auto mb-4 text-muted-foreground opacity-50" />
            <h3 className="text-lg font-medium text-muted-foreground mb-2">No opportunities found</h3>
            <p className="text-sm text-muted-foreground mb-4">
              {isConnected 
                ? "No properties match your current criteria. Try adjusting your filters."
                : "Unable to connect to the backend. Check your connection and try again."
              }
            </p>
            {!isConnected && (
              <Button onClick={testConnection} variant="outline">
                Test Connection
              </Button>
            )}
          </div>
        )}

        {/* Content - Only show when not loading and there are properties */}
        {!loading && properties.length > 0 && (
          <>
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
                         {properties.map((property, index) => (
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
          </>
        )}
      </div>
    </div>
  );
}