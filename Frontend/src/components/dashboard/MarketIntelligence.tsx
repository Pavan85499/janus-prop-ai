import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { 
  TrendingUp, 
  TrendingDown,
  DollarSign,
  Home,
  MapPin,
  Calendar,
  Users,
  BarChart3,
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock
} from "lucide-react";
import { motion } from "framer-motion";

const marketMetrics = [
  {
    title: "Total Properties Analyzed",
    value: "12,847",
    change: "+18.2%",
    trend: "up",
    icon: Home,
    color: "text-ice"
  },
  {
    title: "Average Deal Score",
    value: "78.4",
    change: "+5.1%", 
    trend: "up",
    icon: BarChart3,
    color: "text-gold"
  },
  {
    title: "Market Value ($B)",
    value: "$2.4B",
    change: "+12.7%",
    trend: "up", 
    icon: DollarSign,
    color: "text-success"
  },
  {
    title: "Active Opportunities",
    value: "1,234",
    change: "-3.2%",
    trend: "down",
    icon: TrendingUp,
    color: "text-warning"
  }
];

const topMarkets = [
  { location: "Brooklyn, NY", properties: 2847, avgScore: 84.2, growth: "+15.3%" },
  { location: "Queens, NY", properties: 1923, avgScore: 79.8, growth: "+12.1%" },
  { location: "Bronx, NY", properties: 1456, avgScore: 77.4, growth: "+8.7%" },
  { location: "Manhattan, NY", properties: 892, avgScore: 91.2, growth: "+22.4%" },
  { location: "Staten Island, NY", properties: 634, avgScore: 72.1, growth: "+5.9%" }
];

const aiInsights = [
  {
    type: "opportunity",
    title: "High-Value Distress Cluster Found",
    description: "Identified 47 properties in Brooklyn Heights with 15-25% below-market pricing",
    confidence: 94,
    priority: "high"
  },
  {
    type: "market",
    title: "Queens Rental Demand Surge",
    description: "Rental demand increased 18% QoQ, suggesting strong investment potential",
    confidence: 87,
    priority: "medium"
  },
  {
    type: "risk",
    title: "Legal Risk Alert - Zoning Changes",
    description: "Proposed zoning changes in Lower East Side may affect 12 tracked properties",
    confidence: 78,
    priority: "high"
  }
];

export function MarketIntelligence() {
  return (
    <section className="py-20 bg-background relative z-10">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-12">
          <h2 className="font-display text-3xl font-semibold text-foreground mb-4">
            Global Market Intelligence
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Real-time market analysis powered by our AI agent network, providing institutional-grade insights 
            for smarter investment decisions.
          </p>
        </div>

        {/* Market Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {marketMetrics.map((metric, index) => {
            const IconComponent = metric.icon;
            const isPositive = metric.trend === "up";
            
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: index * 0.1 }}
                className="relative z-20"
              >
                <Card className="bg-card border-border h-full">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="w-10 h-10 rounded-lg bg-secondary flex items-center justify-center shrink-0">
                        <IconComponent className={`w-5 h-5 ${metric.color}`} />
                      </div>
                      <div className="flex items-center gap-1 shrink-0">
                        {isPositive ? (
                          <TrendingUp className="w-4 h-4 text-success" />
                        ) : (
                          <TrendingDown className="w-4 h-4 text-destructive" />
                        )}
                        <span className={`text-sm font-medium ${
                          isPositive ? 'text-success' : 'text-destructive'
                        }`}>
                          {metric.change}
                        </span>
                      </div>
                    </div>
                    <div className="mb-2">
                      <p className="text-2xl font-bold text-foreground break-words">{metric.value}</p>
                    </div>
                    <p className="text-sm text-muted-foreground leading-tight">{metric.title}</p>
                  </CardContent>
                </Card>
              </motion.div>
            );
          })}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
          {/* Top Markets */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="relative z-20"
          >
            <Card className="bg-card border-border h-full">
              <CardHeader className="pb-4">
                <CardTitle className="flex items-center gap-2 text-foreground">
                  <MapPin className="w-5 h-5 text-ice shrink-0" />
                  <span className="truncate">Top Markets by Opportunity</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {topMarkets.map((market, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-secondary rounded-lg min-h-[60px]">
                    <div className="flex-1 min-w-0 pr-3">
                      <p className="font-medium text-foreground truncate">{market.location}</p>
                      <p className="text-sm text-muted-foreground truncate">
                        {market.properties.toLocaleString()} properties • Score: {market.avgScore}
                      </p>
                    </div>
                    <div className="shrink-0">
                      <Badge variant="outline" className="border-success text-success whitespace-nowrap">
                        {market.growth}
                      </Badge>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </motion.div>

          {/* AI Insights */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="relative z-20"
          >
            <Card className="bg-card border-border h-full">
              <CardHeader className="pb-4">
                <CardTitle className="flex items-center gap-2 text-foreground">
                  <Activity className="w-5 h-5 text-gold shrink-0" />
                  <span className="truncate">AI Market Insights</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {aiInsights.map((insight, index) => {
                  const getIcon = () => {
                    switch (insight.type) {
                      case 'opportunity': return <TrendingUp className="w-4 h-4 text-success" />;
                      case 'risk': return <AlertTriangle className="w-4 h-4 text-destructive" />;
                      default: return <BarChart3 className="w-4 h-4 text-ice" />;
                    }
                  };

                  const getPriorityColor = () => {
                    switch (insight.priority) {
                      case 'high': return 'border-destructive/30 bg-destructive/5';
                      case 'medium': return 'border-warning/30 bg-warning/5';
                      default: return 'border-border bg-secondary';
                    }
                  };

                  return (
                    <div key={index} className={`p-4 border rounded-lg ${getPriorityColor()} relative`}>
                      <div className="flex items-start gap-3">
                        <div className="mt-0.5 shrink-0">
                          {getIcon()}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between mb-2 gap-2">
                            <h4 className="font-medium text-foreground leading-tight flex-1">{insight.title}</h4>
                            <Badge 
                              variant="outline" 
                              className={`shrink-0 ${insight.priority === 'high' ? 'border-destructive text-destructive' : 'border-warning text-warning'}`}
                            >
                              {insight.priority}
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground mb-3 leading-relaxed">{insight.description}</p>
                          <div className="flex items-center justify-between gap-2">
                            <span className="text-xs text-muted-foreground shrink-0">Confidence</span>
                            <div className="flex items-center gap-2 shrink-0">
                              <Progress value={insight.confidence} className="w-16 h-1" />
                              <span className="text-xs font-medium text-foreground">{insight.confidence}%</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Real-time Activity Feed */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="relative z-20"
        >
          <Card className="bg-card border-border">
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center gap-2 text-foreground">
                <Clock className="w-5 h-5 text-ice shrink-0" />
                <span className="truncate">Real-time Market Activity</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center p-4 bg-secondary rounded-lg min-h-[100px] flex flex-col justify-center">
                  <div className="text-2xl font-bold text-ice mb-1">47</div>
                  <div className="text-sm text-muted-foreground leading-tight">New Properties Analyzed</div>
                  <div className="text-xs text-success mt-1">Last hour</div>
                </div>
                <div className="text-center p-4 bg-secondary rounded-lg min-h-[100px] flex flex-col justify-center">
                  <div className="text-2xl font-bold text-gold mb-1">23</div>
                  <div className="text-sm text-muted-foreground leading-tight">High-Opportunity Flags</div>
                  <div className="text-xs text-success mt-1">Last hour</div>
                </div>
                <div className="text-center p-4 bg-secondary rounded-lg min-h-[100px] flex flex-col justify-center">
                  <div className="text-2xl font-bold text-success mb-1">12</div>
                  <div className="text-sm text-muted-foreground leading-tight">Investment Reports Generated</div>
                  <div className="text-xs text-success mt-1">Last hour</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </section>
  );
}