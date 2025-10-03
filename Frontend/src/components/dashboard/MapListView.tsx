import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Map, List, Star, Eye, MoreHorizontal, RefreshCw, AlertCircle } from "lucide-react";
import { motion } from "framer-motion";
import { useRealEstateAPIs } from "@/hooks/useRealEstateAPIs";
import GooglePropertyMap, { GMapMarker } from "@/components/dashboard/GooglePropertyMap";
import PortfolioMap, { PortfolioMapMarker } from "@/components/dashboard/PortfolioMap";

interface Property {
  id: string;
  address: string;
  price: number;
  estimatedValue: number;
  equity: number;
  type: string;
  beds: number;
  baths: number;
  sqft: number;
  janusScore: number;
  distressLevel: string;
  image: string;
  daysOnMarket?: number;
}

interface MapListViewProps {
  onPropertySelect: (property: Property) => void;
  onPropertyDetail: (property: Property) => void;
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
    image: "/placeholder.svg",
    lat: prop.latitude,
    lng: prop.longitude
  }));

  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY as string | undefined;
  const center = (() => {
    const withCoords = properties.find(p => p.lat && p.lng);
    return withCoords ? { lat: Number(withCoords.lat), lng: Number(withCoords.lng) } : { lat: 40.7128, lng: -74.0060 };
  })();

  const osmMarkers: PortfolioMapMarker[] = properties.filter(p => p.lat && p.lng).map(p => ({
    id: p.id,
    position: { lat: Number(p.lat), lng: Number(p.lng) },
    label: p.address,
    subtitle: `${p.janusScore} score`,
    score: p.janusScore
  }));

  return (
    <div className="flex-1 flex flex-col bg-background min-h-0">
      {/* View Toggle Header */}
      <div className="responsive-padding border-b border-border bg-card">
        <div className="responsive-flex-between">
          <div className="flex-1 min-w-0">
            <h2 className="responsive-heading font-semibold text-foreground mb-2">
              Live Deal Pipeline
            </h2>
            <div className="responsive-flex items-center gap-2 sm:gap-4">
              <p className="responsive-body text-muted-foreground leading-relaxed">
                {properties.length} properties match your criteria
                {lastUpdated && (
                  <span className="ml-2 responsive-caption text-muted-foreground">
                    • Updated {lastUpdated.toLocaleTimeString()}
                  </span>
                )}
              </p>
              <div className="responsive-flex items-center gap-2">
                {!isConnected && (
                  <Badge variant="destructive" className="responsive-caption">
                    <AlertCircle className="w-3 h-3 mr-1" />
                    <span className="mobile-only">Off</span>
                    <span className="tablet-up">Offline</span>
                  </Badge>
                )}
                <Button
                  size="sm"
                  variant="outline"
                  onClick={refreshProperties}
                  disabled={loading}
                  className="touch-target h-7 px-2"
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
              className={`${viewMode === 'map' ? 'bg-ice text-ice-foreground' : 'hover:bg-background/50'} transition-all duration-200 touch-target`}
            >
              <Map className="w-4 h-4 mr-2" />
              <span className="mobile-only">M</span>
              <span className="tablet-up">Map</span>
            </Button>
            <Button
              variant={viewMode === 'list' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('list')}
              className={`${viewMode === 'list' ? 'bg-ice text-ice-foreground' : 'hover:bg-background/50'} transition-all duration-200 touch-target`}
            >
              <List className="w-4 h-4 mr-2" />
              <span className="mobile-only">L</span>
              <span className="tablet-up">List</span>
            </Button>
          </div>
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 responsive-padding overflow-y-auto">
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
            <span className="ml-3 text-muted-foreground">Loading deals...</span>
          </div>
        )}

        {/* Content */}
        {!loading && (
          viewMode === 'map' ? (
            <div className="h-full bg-muted rounded-lg border border-border">
              {apiKey ? (
                <GooglePropertyMap
                  apiKey={apiKey}
                  center={center}
                  markers={properties.filter(p => p.lat && p.lng).map(p => ({
                    id: p.id,
                    position: { lat: Number(p.lat), lng: Number(p.lng) },
                    label: p.address,
                    subtitle: `${p.janusScore} score`,
                    score: p.janusScore
                  }) as GMapMarker)}
                  height={420}
                />
              ) : (
                <PortfolioMap
                  center={center}
                  markers={osmMarkers}
                  height={420}
                />
              )}
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
                    className="bg-card border-border hover:border-ice/50 transition-all duration-200 cursor-pointer touch-friendly"
                    onClick={() => onPropertySelect(property as any)}
                  >
                    <CardContent className="responsive-padding">
                      <div className="responsive-flex gap-4 sm:gap-6">
                        {/* Property Image */}
                        <div className="w-full sm:w-32 h-32 sm:h-24 bg-muted rounded-lg shrink-0 overflow-hidden">
                          <img 
                            src={property.image} 
                            alt={property.address}
                            className="w-full h-full object-cover"
                          />
                        </div>

                        {/* Property Details */}
                        <div className="flex-1 min-w-0">
                          <div className="responsive-flex-between mb-3">
                            <div className="flex-1 min-w-0">
                              <h3 className="responsive-body font-medium text-foreground mb-1 truncate">
                                {property.address}
                              </h3>
                              <div className="responsive-flex items-center gap-2 sm:gap-4 responsive-caption text-muted-foreground">
                                <span>{property.beds} bed</span>
                                <span>{property.baths} bath</span>
                                <span>{property.sqft.toLocaleString()} sqft</span>
                                <span className="mobile-only hidden sm:inline">{property.type}</span>
                              </div>
                              <div className="mobile-only mt-1">
                                <span className="responsive-caption text-muted-foreground">{property.type}</span>
                              </div>
                            </div>
                            <div className="responsive-flex items-center gap-2">
                              <Badge className={`${getScoreColor(property.janusScore)} responsive-caption`}>
                                <span className="mobile-only">{property.janusScore}</span>
                                <span className="tablet-up">Score: {property.janusScore}</span>
                              </Badge>
                              <Badge 
                                variant="outline" 
                                className={`${getDistressColor(property.distressLevel)} responsive-caption`}
                              >
                                <span className="mobile-only">{property.distressLevel}</span>
                                <span className="tablet-up">{property.distressLevel} Distress</span>
                              </Badge>
                            </div>
                          </div>

                          <div className="responsive-grid-2 sm:grid-cols-4 gap-3 sm:gap-4 mb-4">
                            <div>
                              <p className="responsive-caption text-muted-foreground mb-1">List Price</p>
                              <p className="responsive-body font-semibold text-foreground">
                                ${property.price.toLocaleString()}
                              </p>
                            </div>
                            <div>
                              <p className="responsive-caption text-muted-foreground mb-1">Est. Value</p>
                              <p className="responsive-body font-semibold text-ice">
                                ${property.estimatedValue.toLocaleString()}
                              </p>
                            </div>
                            <div>
                              <p className="responsive-caption text-muted-foreground mb-1">Equity</p>
                              <p className="responsive-body font-semibold text-gold">
                                {property.equity}%
                              </p>
                            </div>
                            <div>
                              <p className="responsive-caption text-muted-foreground mb-1">Potential Gain</p>
                              <p className="responsive-body font-semibold text-success">
                                ${(property.estimatedValue - property.price).toLocaleString()}
                              </p>
                            </div>
                          </div>

                          <div className="responsive-flex-between">
                            <div className="responsive-flex items-center gap-2 sm:gap-4">
                              <Button 
                                size="sm" 
                                variant="outline" 
                                className="border-border hover:bg-muted touch-target"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  onPropertyDetail(property as any);
                                }}
                              >
                                <Eye className="w-4 h-4 mr-2" />
                                <span className="mobile-only">View</span>
                                <span className="tablet-up">View Details</span>
                              </Button>
                              <Button size="sm" variant="ghost" className="hover:bg-muted touch-target">
                                <Star className="w-4 h-4 mr-2" />
                                <span className="mobile-only">Save</span>
                                <span className="tablet-up">Save</span>
                              </Button>
                            </div>
                            <Button size="sm" variant="ghost" className="hover:bg-muted touch-target">
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
          )
        )}
      </div>
    </div>
  );
}