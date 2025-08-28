import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { 
  Clock, 
  Calendar,
  CheckCircle,
  AlertCircle,
  Phone,
  Mail,
  FileText,
  DollarSign,
  Eye,
  Star,
  MoreHorizontal,
  Bot,
  TrendingDown,
  TrendingUp
} from "lucide-react";
import { motion } from "framer-motion";

const mockLeads = [
  {
    id: 1,
    address: "123 Oak Street, Brooklyn, NY",
    savedDate: "2024-01-15",
    status: "offer-drafted",
    lastActivity: "Offer Drafted",
    lastActivityDate: "Jan 20, 2024",
    nextAction: "Follow up with owner",
    agentTip: "Valyria: Owner engagement patterns suggest 15% price reduction possible. Market timing favors quick action.",
    price: 485000,
    estimatedValue: 620000,
    image: "/placeholder.svg",
    priority: "high",
    daysInPipeline: 12,
    notes: 3
  },
  {
    id: 2,
    address: "456 Maple Ave, Queens, NY",
    savedDate: "2024-01-10",
    status: "contacted-owner",
    lastActivity: "Owner Contacted",
    lastActivityDate: "Jan 18, 2024",
    nextAction: "Schedule property viewing",
    agentTip: "Eden: Price dropped 5% - revise offer strategy. Osiris updated projections show improved IRR.",
    price: 325000,
    estimatedValue: 415000,
    image: "/placeholder.svg",
    priority: "medium",
    daysInPipeline: 18,
    notes: 5
  },
  {
    id: 3,
    address: "789 Pine Road, Bronx, NY",
    savedDate: "2024-01-08",
    status: "analysis-complete",
    lastActivity: "Analysis Complete",
    lastActivityDate: "Jan 16, 2024",
    nextAction: "Contact property owner",
    agentTip: "Spring: Data validation complete. Elysia enriched with new comparables. Atelius confirms clean title.",
    price: 195000,
    estimatedValue: 280000,
    image: "/placeholder.svg",
    priority: "high",
    daysInPipeline: 22,
    notes: 2
  }
];

const statusConfig = {
  "analysis-complete": { 
    label: "Analysis Complete", 
    color: "bg-ice/20 text-ice border-ice/30",
    icon: CheckCircle
  },
  "contacted-owner": { 
    label: "Owner Contacted", 
    color: "bg-warning/20 text-warning border-warning/30",
    icon: Phone
  },
  "offer-drafted": { 
    label: "Offer Drafted", 
    color: "bg-gold/20 text-gold border-gold/30",
    icon: FileText
  },
  "under-review": { 
    label: "Under Review", 
    color: "bg-success/20 text-success border-success/30",
    icon: Eye
  }
};

const priorityConfig = {
  "high": { color: "bg-destructive/20 text-destructive border-destructive/30", label: "High" },
  "medium": { color: "bg-warning/20 text-warning border-warning/30", label: "Medium" },
  "low": { color: "bg-muted text-muted-foreground border-border", label: "Low" }
};

export function LeadManagement() {
  const [leads] = useState(mockLeads);
  const [sortBy, setSortBy] = useState<'recent' | 'priority' | 'days'>('recent');

  const sortedLeads = [...leads].sort((a, b) => {
    switch (sortBy) {
      case 'priority':
        const priorityOrder = { high: 3, medium: 2, low: 1 };
        return priorityOrder[b.priority as keyof typeof priorityOrder] - 
               priorityOrder[a.priority as keyof typeof priorityOrder];
      case 'days':
        return b.daysInPipeline - a.daysInPipeline;
      default:
        return new Date(b.lastActivityDate).getTime() - new Date(a.lastActivityDate).getTime();
    }
  });

  return (
    <section className="py-20 bg-background">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-12">
          <h2 className="font-display text-3xl font-semibold text-foreground mb-4">
            Lead Management Dashboard
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Track your property pipeline with AI-powered insights and automated follow-up suggestions.
          </p>
        </div>

        <Card className="bg-card border-border">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2 text-foreground">
                <Star className="w-5 h-5 text-gold" />
                Saved Leads ({leads.length})
              </CardTitle>
              <div className="flex items-center gap-2">
                <Button
                  variant={sortBy === 'recent' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSortBy('recent')}
                  className={sortBy === 'recent' ? 'bg-ice text-ice-foreground' : 'border-border'}
                >
                  Recent
                </Button>
                <Button
                  variant={sortBy === 'priority' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSortBy('priority')}
                  className={sortBy === 'priority' ? 'bg-ice text-ice-foreground' : 'border-border'}
                >
                  Priority
                </Button>
                <Button
                  variant={sortBy === 'days' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSortBy('days')}
                  className={sortBy === 'days' ? 'bg-ice text-ice-foreground' : 'border-border'}
                >
                  Pipeline Time
                </Button>
              </div>
            </div>
          </CardHeader>
          
          <CardContent className="p-0">
            <ScrollArea className="h-[600px]">
              <div className="space-y-0">
                {sortedLeads.map((lead, index) => {
                  const statusInfo = statusConfig[lead.status as keyof typeof statusConfig];
                  const priorityInfo = priorityConfig[lead.priority as keyof typeof priorityConfig];
                  const StatusIcon = statusInfo.icon;
                  const equityGain = lead.estimatedValue - lead.price;
                  const equityPercentage = ((equityGain / lead.price) * 100).toFixed(1);

                  return (
                    <motion.div
                      key={lead.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.1 }}
                      className="border-b border-border last:border-b-0"
                    >
                      <div className="p-6 hover:bg-muted/30 transition-colors">
                        {/* Timeline Connection */}
                        {index < sortedLeads.length - 1 && (
                          <div className="absolute left-8 mt-20 w-px h-8 bg-border" />
                        )}
                        
                        <div className="flex gap-6">
                          {/* Timeline Dot */}
                          <div className="relative">
                            <div className="w-3 h-3 bg-ice rounded-full mt-2" />
                          </div>

                          {/* Property Image */}
                          <div className="w-20 h-16 bg-muted rounded-lg shrink-0 overflow-hidden">
                            <img 
                              src={lead.image} 
                              alt={lead.address}
                              className="w-full h-full object-cover"
                            />
                          </div>

                          {/* Lead Details */}
                          <div className="flex-1 min-w-0">
                            <div className="flex items-start justify-between mb-3">
                              <div>
                                <h3 className="font-medium text-foreground mb-1">
                                  {lead.address}
                                </h3>
                                <div className="flex items-center gap-3 text-sm text-muted-foreground">
                                  <span>Saved {lead.savedDate}</span>
                                  <span>•</span>
                                  <span>{lead.daysInPipeline} days in pipeline</span>
                                  <span>•</span>
                                  <span>{lead.notes} notes</span>
                                </div>
                              </div>
                              <div className="flex items-center gap-2">
                                <Badge variant="outline" className={priorityInfo.color}>
                                  {priorityInfo.label} Priority
                                </Badge>
                                <Badge variant="outline" className={statusInfo.color}>
                                  <StatusIcon className="w-3 h-3 mr-1" />
                                  {statusInfo.label}
                                </Badge>
                              </div>
                            </div>

                            <div className="grid grid-cols-4 gap-4 mb-3">
                              <div>
                                <p className="text-xs text-muted-foreground mb-1">List Price</p>
                                <p className="font-semibold text-foreground text-sm">
                                  ${lead.price.toLocaleString()}
                                </p>
                              </div>
                              <div>
                                <p className="text-xs text-muted-foreground mb-1">Est. Value</p>
                                <p className="font-semibold text-ice text-sm">
                                  ${lead.estimatedValue.toLocaleString()}
                                </p>
                              </div>
                              <div>
                                <p className="text-xs text-muted-foreground mb-1">Potential Gain</p>
                                <p className="font-semibold text-gold text-sm">
                                  ${equityGain.toLocaleString()} ({equityPercentage}%)
                                </p>
                              </div>
                              <div>
                                <p className="text-xs text-muted-foreground mb-1">Last Activity</p>
                                <p className="font-medium text-foreground text-sm">
                                  {lead.lastActivityDate}
                                </p>
                              </div>
                            </div>

                            {/* AI Agent Tip */}
                            <Card className="bg-secondary/50 border-border mb-3">
                              <CardContent className="p-3">
                                <div className="flex items-start gap-2">
                                  <Bot className="w-4 h-4 text-ice mt-0.5 shrink-0" />
                                  <p className="text-sm text-foreground italic">
                                    {lead.agentTip}
                                  </p>
                                </div>
                              </CardContent>
                            </Card>

                            {/* Actions */}
                            <div className="flex items-center gap-3">
                              <div className="flex items-center gap-3">
                                <Button size="sm" variant="outline" className="border-border hover:bg-muted">
                                  <Phone className="w-4 h-4 mr-2" />
                                  Contact (Valyria)
                                </Button>
                                <Button size="sm" variant="outline" className="border-border hover:bg-muted">
                                  <FileText className="w-4 h-4 mr-2" />
                                  Update Analysis (Celestia)
                                </Button>
                                <Button size="sm" variant="outline" className="border-border hover:bg-muted">
                                  <Calendar className="w-4 h-4 mr-2" />
                                  Schedule (Aurora)
                                </Button>
                              </div>
                              <div className="flex items-center gap-2">
                                <Button size="sm" variant="ghost" className="hover:bg-muted">
                                  <MoreHorizontal className="w-4 h-4" />
                                </Button>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      </div>
    </section>
  );
}