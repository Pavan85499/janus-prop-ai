import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { 
  Search, 
  Filter, 
  Eye, 
  Star, 
  Archive, 
  TrendingUp,
  MapPin,
  DollarSign,
  RefreshCw,
  AlertCircle
} from "lucide-react";
import { useRealEstateAPIs } from "@/hooks/useRealEstateAPIs";

const mockDeals = [
  {
    id: 1,
    address: "1247 Oak Street, Austin, TX",
    lienScore: 94,
    capRate: 12.4,
    strategy: "Buy-to-Hold",
    aiSummary: "Prime location with strong rental demand. Tax lien provides 35% discount to market value.",
    risk: "low",
    price: "$185,000",
    rentEstimate: "$2,100/mo"
  },
  {
    id: 2,
    address: "892 Pine Avenue, Houston, TX", 
    lienScore: 87,
    capRate: 10.8,
    strategy: "BRRRR",
    aiSummary: "Distressed property in gentrifying neighborhood. High renovation potential.",
    risk: "medium",
    price: "$145,000",
    rentEstimate: "$1,800/mo"
  },
  {
    id: 3,
    address: "3456 Elm Drive, Dallas, TX",
    lienScore: 76,
    capRate: 8.9,
    strategy: "Cap Rate Arbitrage",
    aiSummary: "Stable cash flow opportunity in established residential area.",
    risk: "low", 
    price: "$225,000",
    rentEstimate: "$2,400/mo"
  },
  {
    id: 4,
    address: "789 Maple Court, San Antonio, TX",
    lienScore: 91,
    capRate: 11.2,
    strategy: "Buy-to-Hold",
    aiSummary: "Recently renovated duplex with dual income streams. Owner motivated.",
    risk: "low",
    price: "$165,000", 
    rentEstimate: "$1,950/mo"
  },
  {
    id: 5,
    address: "555 Cedar Lane, Fort Worth, TX",
    lienScore: 68,
    capRate: 7.3,
    strategy: "Long-term Hold",
    aiSummary: "Growing suburban market with planned infrastructure improvements.",
    risk: "medium",
    price: "$198,000",
    rentEstimate: "$1,750/mo"
  },
];

interface DealTableProps {
  onPropertySelect: (property: any) => void;
}

export function DealTable({ onPropertySelect }: DealTableProps) {
  const [searchTerm, setSearchTerm] = useState("");
  
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

  // Convert real estate APIs data to deal format
  const deals = realEstateProperties.map(prop => ({
    id: prop.id,
    address: prop.address,
    lienScore: Math.round((prop.api_confidence || 0.8) * 100), // Convert API confidence to score
    capRate: prop.estimated_value && prop.price ? ((prop.estimated_value - prop.price) / prop.price * 100) : 8.5,
    strategy: prop.market_trend === "Rising" ? "Buy-to-Hold" : prop.market_trend === "Stable" ? "BRRRR" : "Quick Flip",
    aiSummary: `AI Analysis: ${prop.market_trend} market trend with ${prop.api_confidence ? Math.round(prop.api_confidence * 100) : 80}% confidence. Data source: ${prop.data_source}`,
    risk: prop.market_trend === "Declining" ? "high" : prop.market_trend === "Stable" ? "medium" : "low",
    price: `$${prop.price ? prop.price.toLocaleString() : 'N/A'}`,
    rentEstimate: prop.price ? `$${Math.round(prop.price * 0.01).toLocaleString()}/mo` : 'N/A'
  }));
  const [sortBy, setSortBy] = useState("lienScore");

  const getScoreColor = (score: number) => {
    if (score >= 85) return "score-high";
    if (score >= 70) return "score-medium"; 
    return "score-low";
  };

  const getRiskBadge = (risk: string) => {
    const variants = {
      low: "bg-success/20 text-success border-success/30",
      medium: "bg-warning/20 text-warning border-warning/30", 
      high: "bg-destructive/20 text-destructive border-destructive/30"
    };
    return variants[risk as keyof typeof variants] || variants.medium;
  };

  const filteredDeals = deals.filter(deal =>
    deal.address.toLowerCase().includes(searchTerm.toLowerCase()) ||
    deal.strategy.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-display text-2xl font-normal">Live Deal Pipeline</h2>
                     <p className="text-muted-foreground mt-1">
             {filteredDeals.length} opportunities • {lastUpdated ? `Updated ${lastUpdated.toLocaleTimeString()}` : 'Loading...'}
           </p>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input 
              placeholder="Search properties..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 w-64 bg-secondary/20 border-border/50"
            />
          </div>
          
          <Button variant="outline" size="sm">
            <Filter className="w-4 h-4 mr-2" />
            Filter
          </Button>
        </div>
      </div>

      <Card className="data-card">
        <CardHeader>
                  <CardTitle className="flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-primary" />
          Investment Opportunities
          {lastUpdated && (
            <span className="text-sm font-normal text-muted-foreground">
              • Updated {lastUpdated.toLocaleTimeString()}
            </span>
          )}
        </CardTitle>
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
        </CardHeader>
        
        <CardContent className="p-0">
          {/* Error Display */}
          {error && (
            <div className="p-4 bg-destructive/10 border-b border-destructive/20">
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
            <div className="flex items-center justify-center py-8">
              <RefreshCw className="w-6 h-6 animate-spin text-muted-foreground" />
              <span className="ml-2 text-muted-foreground">Loading opportunities...</span>
            </div>
          )}

          {/* No Data State */}
          {!loading && deals.length === 0 && (
            <div className="text-center py-8">
              <TrendingUp className="w-8 h-8 mx-auto mb-2 text-muted-foreground opacity-50" />
              <p className="text-sm text-muted-foreground">
                {isConnected 
                  ? "No investment opportunities found. Try adjusting your filters."
                  : "Unable to connect to the backend. Check your connection and try again."
                }
              </p>
              {!isConnected && (
                <Button onClick={testConnection} variant="outline" className="mt-2">
                  Test Connection
                </Button>
              )}
            </div>
          )}

          {/* Table Content - Only show when not loading and there are deals */}
          {!loading && deals.length > 0 && (
            <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="border-b border-border/30">
                  <TableHead className="w-[280px] min-w-[280px]">Property</TableHead>
                  <TableHead className="w-[100px] text-center">Lien Score</TableHead>
                  <TableHead className="w-[100px] text-center">Cap Rate</TableHead>
                  <TableHead className="w-[140px]">Strategy</TableHead>
                  <TableHead className="w-[300px] min-w-[300px]">AI Summary</TableHead>
                  <TableHead className="w-[120px] text-center">Actions</TableHead>
                </TableRow>
              </TableHeader>
              
              <TableBody>
                {filteredDeals.map((deal) => (
                  <TableRow 
                    key={deal.id} 
                    className="deal-row cursor-pointer"
                    onClick={() => onPropertySelect(deal)}
                  >
                    <TableCell className="w-[280px] min-w-[280px]">
                      <div className="space-y-1">
                        <div className="font-medium text-sm leading-tight break-words">
                          {deal.address}
                        </div>
                        <div className="flex items-center gap-3 text-xs text-muted-foreground">
                          <span className="flex items-center gap-1 whitespace-nowrap">
                            <DollarSign className="w-3 h-3 flex-shrink-0" />
                            {deal.price}
                          </span>
                          <span className="flex items-center gap-1 whitespace-nowrap">
                            <MapPin className="w-3 h-3 flex-shrink-0" />
                            {deal.rentEstimate}
                          </span>
                        </div>
                      </div>
                    </TableCell>
                    
                    <TableCell className="w-[100px] text-center">
                      <Badge className={`${getScoreColor(deal.lienScore)} font-mono text-xs`}>
                        {deal.lienScore}
                      </Badge>
                    </TableCell>
                    
                    <TableCell className="w-[100px] text-center">
                      <span className="font-mono text-success font-medium text-sm">
                        {deal.capRate}%
                      </span>
                    </TableCell>
                    
                    <TableCell className="w-[140px]">
                      <Badge 
                        variant="outline" 
                        className="bg-primary/10 text-primary border-primary/30 text-xs whitespace-nowrap"
                      >
                        {deal.strategy}
                      </Badge>
                    </TableCell>
                    
                    <TableCell className="w-[300px] min-w-[300px]">
                      <div className="text-sm text-muted-foreground leading-relaxed break-words">
                        {deal.aiSummary}
                      </div>
                    </TableCell>
                    
                    <TableCell className="w-[120px]">
                      <div className="flex items-center justify-center gap-1">
                        <Button 
                          size="sm" 
                          variant="ghost"
                          className="h-8 w-8 p-0"
                          onClick={(e) => {
                            e.stopPropagation();
                            onPropertySelect(deal);
                          }}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        
                        <Button 
                          size="sm" 
                          variant="ghost"
                          className="h-8 w-8 p-0"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <Star className="w-4 h-4" />
                        </Button>
                        
                        <Button 
                          size="sm" 
                          variant="ghost"
                          className="h-8 w-8 p-0"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <Archive className="w-4 h-4" />
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
  );
}