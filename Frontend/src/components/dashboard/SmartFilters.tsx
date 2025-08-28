import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { 
  Brain, 
  TrendingUp, 
  AlertTriangle, 
  DollarSign, 
  MapPin, 
  Home, 
  Filter,
  ChevronDown,
  Star,
  Zap
} from "lucide-react";

const aiRecommendations = [
  { label: "Eden Highly Recommended", icon: Star, count: 47, active: true },
  { label: "Orion High Distress Score", icon: AlertTriangle, count: 23, active: false },
  { label: "Valyria Strong Rental Potential", icon: TrendingUp, count: 31, active: false },
  { label: "Osiris Quick Flip Opportunities", icon: Zap, count: 18, active: false }
];

export function SmartFilters() {
  const [priceRange, setPriceRange] = useState([100000, 800000]);
  const [equityRange, setEquityRange] = useState([20, 80]);
  const [offMarketOnly, setOffMarketOnly] = useState(false);
  const [distressScore, setDistressScore] = useState(false);
  const [rentalPotential, setRentalPotential] = useState(false);
  const [expandedSections, setExpandedSections] = useState({
    ai: true,
    location: false,
    property: false,
    financial: false
  });

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections(prev => ({ ...prev, [section]: !prev[section] }));
  };

  return (
    <div className="w-80 h-screen bg-card border-r border-border p-6 overflow-y-auto">
      <div className="flex items-center gap-3 mb-6">
        <Filter className="w-5 h-5 text-ice" />
        <h2 className="font-display text-lg font-semibold text-foreground">Smart Filters</h2>
      </div>

      {/* AI Recommendations */}
      <Collapsible 
        open={expandedSections.ai} 
        onOpenChange={() => toggleSection('ai')}
        className="mb-6"
      >
        <CollapsibleTrigger asChild>
          <Button 
            variant="ghost" 
            className="w-full justify-between p-0 h-auto hover:bg-transparent"
          >
            <div className="flex items-center gap-2">
              <Brain className="w-4 h-4 text-ice" />
              <span className="font-medium text-foreground">Janus AI Recommendations</span>
            </div>
            <ChevronDown className={`w-4 h-4 text-muted-foreground transition-transform ${expandedSections.ai ? 'rotate-180' : ''}`} />
          </Button>
        </CollapsibleTrigger>
        <CollapsibleContent className="mt-4 space-y-3">
          {aiRecommendations.map((rec, index) => {
            const IconComponent = rec.icon;
            return (
              <Button
                key={index}
                variant={rec.active ? "default" : "outline"}
                size="sm"
                className={`w-full justify-between h-auto min-h-[36px] py-2 px-3 ${rec.active ? 'bg-ice text-ice-foreground hover:bg-ice/90' : 'border-border hover:bg-muted'}`}
              >
                <div className="flex items-center gap-2 flex-1 min-w-0">
                  <IconComponent className="w-4 h-4 flex-shrink-0" />
                  <span className="text-xs leading-tight text-left break-words overflow-hidden">
                    {rec.label}
                  </span>
                </div>
                <Badge variant="secondary" className="bg-muted text-muted-foreground ml-2 flex-shrink-0 text-xs">
                  {rec.count}
                </Badge>
              </Button>
            );
          })}
        </CollapsibleContent>
      </Collapsible>

      {/* Key Toggles */}
      <Card className="mb-6 bg-secondary border-border">
        <CardContent className="p-4 space-y-4">
          <div className="flex items-center justify-between">
            <Label htmlFor="off-market" className="text-sm font-medium">Off-Market Only</Label>
            <Switch 
              id="off-market" 
              checked={offMarketOnly} 
              onCheckedChange={setOffMarketOnly}
            />
          </div>
          <div className="flex items-center justify-between">
            <Label htmlFor="distress-score" className="text-sm font-medium">High Distress Score</Label>
            <Switch 
              id="distress-score" 
              checked={distressScore} 
              onCheckedChange={setDistressScore}
            />
          </div>
          <div className="flex items-center justify-between">
            <Label htmlFor="rental-potential" className="text-sm font-medium">Strong Rental Potential</Label>
            <Switch 
              id="rental-potential" 
              checked={rentalPotential} 
              onCheckedChange={setRentalPotential}
            />
          </div>
        </CardContent>
      </Card>

      {/* Location Filters */}
      <Collapsible 
        open={expandedSections.location} 
        onOpenChange={() => toggleSection('location')}
        className="mb-6"
      >
        <CollapsibleTrigger asChild>
          <Button 
            variant="ghost" 
            className="w-full justify-between p-0 h-auto hover:bg-transparent"
          >
            <div className="flex items-center gap-2">
              <MapPin className="w-4 h-4 text-muted-foreground" />
              <span className="font-medium text-foreground">Location</span>
            </div>
            <ChevronDown className={`w-4 h-4 text-muted-foreground transition-transform ${expandedSections.location ? 'rotate-180' : ''}`} />
          </Button>
        </CollapsibleTrigger>
        <CollapsibleContent className="mt-4 space-y-4">
          <div>
            <Label htmlFor="zip-codes" className="text-sm font-medium mb-2 block">Zip Codes</Label>
            <Input 
              id="zip-codes"
              placeholder="10001, 10002, 10003..."
              className="bg-input border-border"
            />
          </div>
          <div>
            <Label htmlFor="neighborhoods" className="text-sm font-medium mb-2 block">Neighborhoods</Label>
            <Select>
              <SelectTrigger className="bg-input border-border">
                <SelectValue placeholder="Select neighborhoods" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="manhattan">Manhattan</SelectItem>
                <SelectItem value="brooklyn">Brooklyn</SelectItem>
                <SelectItem value="queens">Queens</SelectItem>
                <SelectItem value="bronx">Bronx</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CollapsibleContent>
      </Collapsible>

      {/* Property Type */}
      <Collapsible 
        open={expandedSections.property} 
        onOpenChange={() => toggleSection('property')}
        className="mb-6"
      >
        <CollapsibleTrigger asChild>
          <Button 
            variant="ghost" 
            className="w-full justify-between p-0 h-auto hover:bg-transparent"
          >
            <div className="flex items-center gap-2">
              <Home className="w-4 h-4 text-muted-foreground" />
              <span className="font-medium text-foreground">Property Type</span>
            </div>
            <ChevronDown className={`w-4 h-4 text-muted-foreground transition-transform ${expandedSections.property ? 'rotate-180' : ''}`} />
          </Button>
        </CollapsibleTrigger>
        <CollapsibleContent className="mt-4 space-y-4">
          <Select>
            <SelectTrigger className="bg-input border-border">
              <SelectValue placeholder="All property types" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="single-family">Single Family</SelectItem>
              <SelectItem value="multi-family">Multi Family</SelectItem>
              <SelectItem value="condo">Condo</SelectItem>
              <SelectItem value="townhouse">Townhouse</SelectItem>
              <SelectItem value="commercial">Commercial</SelectItem>
            </SelectContent>
          </Select>
        </CollapsibleContent>
      </Collapsible>

      {/* Financial Filters */}
      <Collapsible 
        open={expandedSections.financial} 
        onOpenChange={() => toggleSection('financial')}
        className="mb-6"
      >
        <CollapsibleTrigger asChild>
          <Button 
            variant="ghost" 
            className="w-full justify-between p-0 h-auto hover:bg-transparent"
          >
            <div className="flex items-center gap-2">
              <DollarSign className="w-4 h-4 text-muted-foreground" />
              <span className="font-medium text-foreground">Financial</span>
            </div>
            <ChevronDown className={`w-4 h-4 text-muted-foreground transition-transform ${expandedSections.financial ? 'rotate-180' : ''}`} />
          </Button>
        </CollapsibleTrigger>
        <CollapsibleContent className="mt-4 space-y-6">
          <div>
            <Label className="text-sm font-medium mb-3 block">
              Price Range: ${priceRange[0].toLocaleString()} - ${priceRange[1].toLocaleString()}
            </Label>
            <Slider
              value={priceRange}
              onValueChange={setPriceRange}
              max={2000000}
              min={50000}
              step={25000}
              className="w-full"
            />
          </div>
          <div>
            <Label className="text-sm font-medium mb-3 block">
              Equity %: {equityRange[0]}% - {equityRange[1]}%
            </Label>
            <Slider
              value={equityRange}
              onValueChange={setEquityRange}
              max={100}
              min={0}
              step={5}
              className="w-full"
            />
          </div>
        </CollapsibleContent>
      </Collapsible>

      {/* Reset Filters */}
      <Button 
        variant="outline" 
        className="w-full border-border hover:bg-muted"
        onClick={() => {
          setPriceRange([100000, 800000]);
          setEquityRange([20, 80]);
          setOffMarketOnly(false);
          setDistressScore(false);
          setRentalPotential(false);
        }}
      >
        Reset All Filters
      </Button>
    </div>
  );
}