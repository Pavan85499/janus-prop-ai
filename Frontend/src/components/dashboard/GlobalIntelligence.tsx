import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  TrendingUp, 
  TrendingDown, 
  Building2, 
  Target, 
  DollarSign,
  AlertTriangle,
  Filter,
  Zap
} from "lucide-react";

const stats = [
  {
    title: "Total Properties",
    value: "2,847",
    change: "+12.3%",
    trend: "up",
    icon: Building2,
  },
  {
    title: "Lien Opportunities",
    value: "156",
    change: "+8 today",
    trend: "up",
    icon: Target,
  },
  {
    title: "Avg Cap Rate",
    value: "8.7%",
    change: "+0.3%",
    trend: "up",
    icon: DollarSign,
  },
  {
    title: "High Priority",
    value: "23",
    change: "7 flagged",
    trend: "alert",
    icon: AlertTriangle,
  },
];

const insights = [
  "AI flagged 7 new high-yield properties this morning",
  "Market trend: Cap rates increasing in Austin metro",
  "3 portfolio opportunities require immediate review",
];

export function GlobalIntelligence() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-3xl font-normal">Global Intelligence</h1>
          <p className="text-muted-foreground mt-1">Real-time market analysis and opportunity detection</p>
        </div>
        
        <div className="flex items-center gap-3">
          <Button variant="outline" size="sm">
            <Filter className="w-4 h-4 mr-2" />
            Filter
          </Button>
          <Button variant="default" size="sm" className="bg-gradient-primary glow-primary">
            <Zap className="w-4 h-4 mr-2" />
            Launch Agent
          </Button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <Card key={index} className="data-card">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">{stat.title}</p>
                  <p className="font-display text-2xl font-normal">{stat.value}</p>
                  <div className="flex items-center gap-2">
                    {stat.trend === "up" && <TrendingUp className="w-4 h-4 text-success" />}
                    {stat.trend === "down" && <TrendingDown className="w-4 h-4 text-destructive" />}
                    {stat.trend === "alert" && <AlertTriangle className="w-4 h-4 text-warning" />}
                    <span className={`text-sm ${
                      stat.trend === "up" ? "text-success" : 
                      stat.trend === "down" ? "text-destructive" : 
                      "text-warning"
                    }`}>
                      {stat.change}
                    </span>
                  </div>
                </div>
                <div className={`p-3 rounded-lg ${
                  stat.trend === "alert" ? "bg-warning/20" : "bg-primary/20"
                }`}>
                  <stat.icon className={`w-6 h-6 ${
                    stat.trend === "alert" ? "text-warning" : "text-primary"
                  }`} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Live Insights */}
      <Card className="data-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <div className="w-2 h-2 bg-success rounded-full animate-pulse"></div>
            Live Market Insights
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {insights.map((insight, index) => (
              <div key={index} className="flex items-start gap-3 p-3 bg-secondary/20 rounded-lg">
                <div className="w-1.5 h-1.5 bg-primary rounded-full mt-2 shrink-0"></div>
                <p className="text-sm">{insight}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}