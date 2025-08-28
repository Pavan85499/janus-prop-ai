import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { 
  ChevronDown,
  ChevronRight,
  Database,
  Sparkles,
  Calculator,
  Target,
  Briefcase,
  Play,
  Pause,
  FileText,
  Clock
} from "lucide-react";

const agents = [
  {
    name: "Data Sourcing Agent",
    description: "Monitors multiple listing services and county records",
    status: "running",
    lastUpdate: "2m ago",
    stats: "4,231 properties scanned",
    icon: Database,
    details: [
      "Connected to 12 MLS systems",
      "Real-time courthouse monitoring",
      "Property tax lien detection",
    ]
  },
  {
    name: "Enrichment Agent", 
    description: "Augments property data with market intelligence",
    status: "running",
    lastUpdate: "5m ago",
    stats: "156 properties enriched",
    icon: Sparkles,
    details: [
      "Rental comps analysis",
      "Neighborhood scoring",
      "Investment potential assessment",
    ]
  },
  {
    name: "Underwriting Agent",
    description: "Performs financial analysis and risk assessment",
    status: "idle",
    lastUpdate: "15m ago", 
    stats: "89 deals analyzed",
    icon: Calculator,
    details: [
      "Cap rate calculations",
      "Cash flow projections",
      "Risk factor analysis",
    ]
  },
  {
    name: "Strategy Agent",
    description: "Identifies optimal investment strategies",
    status: "running",
    lastUpdate: "1m ago",
    stats: "23 strategies matched",
    icon: Target,
    details: [
      "Buy-and-hold analysis",
      "BRRRR opportunities",
      "Flip potential scoring",
    ]
  },
  {
    name: "Portfolio Agent",
    description: "Manages portfolio optimization and diversification",
    status: "idle",
    lastUpdate: "32m ago",
    stats: "12 portfolios tracked",
    icon: Briefcase,
    details: [
      "Geographic diversification",
      "Asset class balance",  
      "Risk-return optimization",
    ]
  },
];

export function AgentModules() {
  const [expandedAgents, setExpandedAgents] = useState<string[]>(["Data Sourcing Agent"]);

  const toggleAgent = (agentName: string) => {
    setExpandedAgents(prev => 
      prev.includes(agentName) 
        ? prev.filter(name => name !== agentName)
        : [...prev, agentName]
    );
  };

  const runningAgents = agents.filter(agent => agent.status === "running").length;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-display text-2xl font-normal">Agent Operations</h2>
          <p className="text-muted-foreground mt-1">
            {runningAgents} of {agents.length} agents actively processing
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          <Badge variant="secondary" className="bg-success/20 text-success border-success/30">
            <div className="w-2 h-2 bg-success rounded-full animate-pulse mr-2"></div>
            {runningAgents} Active
          </Badge>
        </div>
      </div>

      <div className="space-y-4">
        {agents.map((agent, index) => (
          <Card key={index} className="data-card">
            <Collapsible 
              open={expandedAgents.includes(agent.name)}
              onOpenChange={() => toggleAgent(agent.name)}
            >
              <CollapsibleTrigger asChild>
                <CardHeader className="cursor-pointer hover:bg-secondary/20 transition-colors rounded-t-lg">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className={`p-2 rounded-lg ${
                        agent.status === "running" ? "bg-success/20" : "bg-muted/20"
                      }`}>
                        <agent.icon className={`w-5 h-5 ${
                          agent.status === "running" ? "text-success" : "text-muted-foreground"
                        }`} />
                      </div>
                      
                      <div>
                        <CardTitle className="text-lg font-normal">{agent.name}</CardTitle>
                        <p className="text-sm text-muted-foreground">{agent.description}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <div className={`agent-status ${agent.status}`}>
                          {agent.status === "running" ? (
                            <Play className="w-3 h-3" />
                          ) : (
                            <Pause className="w-3 h-3" />
                          )}
                          {agent.status}
                        </div>
                        <p className="text-xs text-muted-foreground mt-1">
                          Updated {agent.lastUpdate}
                        </p>
                      </div>
                      
                      {expandedAgents.includes(agent.name) ? (
                        <ChevronDown className="w-5 h-5 text-muted-foreground" />
                      ) : (
                        <ChevronRight className="w-5 h-5 text-muted-foreground" />
                      )}
                    </div>
                  </div>
                </CardHeader>
              </CollapsibleTrigger>
              
              <CollapsibleContent>
                <CardContent className="pt-0">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-medium mb-3">Current Activity</h4>
                      <p className="text-sm text-muted-foreground mb-4">{agent.stats}</p>
                      
                      <div className="space-y-2">
                        {agent.details.map((detail, idx) => (
                          <div key={idx} className="flex items-center gap-2 text-sm">
                            <div className="w-1.5 h-1.5 bg-primary rounded-full"></div>
                            {detail}
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    <div className="space-y-3">
                      <div className="flex gap-2">
                        <Button 
                          size="sm" 
                          variant={agent.status === "running" ? "destructive" : "default"}
                          className="flex-1"
                        >
                          {agent.status === "running" ? (
                            <>
                              <Pause className="w-4 h-4 mr-2" />
                              Pause
                            </>
                          ) : (
                            <>
                              <Play className="w-4 h-4 mr-2" />
                              Start
                            </>
                          )}
                        </Button>
                        
                        <Button size="sm" variant="outline">
                          <FileText className="w-4 h-4 mr-2" />
                          Logs
                        </Button>
                      </div>
                      
                      <div className="p-3 bg-secondary/20 rounded-lg">
                        <div className="flex items-center gap-2 text-sm">
                          <Clock className="w-4 h-4 text-muted-foreground" />
                          <span className="text-muted-foreground">Next run:</span>
                          <span>In 12 minutes</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </CollapsibleContent>
            </Collapsible>
          </Card>
        ))}
      </div>
    </div>
  );
}