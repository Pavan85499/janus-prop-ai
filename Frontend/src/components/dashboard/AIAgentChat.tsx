import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  MessageSquare, 
  Send, 
  Bot, 
  User, 
  Calculator,
  FileText,
  Phone,
  TrendingUp,
  Brain,
  Search,
  Shield,
  Database,
  GitBranch,
  CheckCircle
} from "lucide-react";
import { motion } from "framer-motion";

const agentProfiles = {
  "Eden": {
    icon: Brain,
    color: "text-gold",
    bgColor: "bg-gold/10",
    role: "Executive Strategist",
    specialty: "Makes final investment decisions using all agent signals and ranks deals by return and fit"
  },
  "Orion": {
    icon: Search,
    color: "text-ice",
    bgColor: "bg-ice/10", 
    role: "Market Intelligence Scanner",
    specialty: "Monitors and collects tax liens, auctions, violations, and court activity in real time"
  },
  "Atelius": {
    icon: Shield,
    color: "text-success",
    bgColor: "bg-success/10",
    role: "Legal Intelligence Agent", 
    specialty: "Parses court filings, redemption rules, legal risks, and title chains"
  },
  "Osiris": {
    icon: Calculator,
    color: "text-warning",
    bgColor: "bg-warning/10",
    role: "Financial Modeler",
    specialty: "Projects returns, redemption windows, and yield forecasts on every deal"
  },
  "Celestia": {
    icon: FileText,
    color: "text-ice",
    bgColor: "bg-ice/10",
    role: "Report Generator",
    specialty: "Creates investor-ready memos, overviews, and PDFs for every opportunity"
  },
  "Valyria": {
    icon: TrendingUp,
    color: "text-gold",
    bgColor: "bg-gold/10",
    role: "Market Forecaster", 
    specialty: "Analyzes migration, rental demand, and zip-code-level shifts to predict price movement"
  },
  "Spring": {
    icon: CheckCircle,
    color: "text-success",
    bgColor: "bg-success/10",
    role: "Quality Control & Audit Agent",
    specialty: "Reviews all outputs for accuracy, completeness, and logic"
  },
  "Elysia": {
    icon: Database,
    color: "text-ice",
    bgColor: "bg-ice/10",
    role: "Data Integrator",
    specialty: "Cleans, enriches, and joins external data (e.g., Redfin, Zillow, gov filings)"
  },
  "Aurora": {
    icon: GitBranch,
    color: "text-gold",
    bgColor: "bg-gold/10",
    role: "Workflow Orchestrator",
    specialty: "Coordinates all agents, routes tasks, and ensures real-time flow of intelligence"
  }
};

const mockConversations = [
  {
    id: 1,
    agent: "Eden",
    message: "I've analyzed the Oak Street property using signals from all agents. The numbers show a 12.4% IRR with low risk profile. This should be prioritized over the Maple Ave deal based on our scoring matrix.",
    timestamp: "2 min ago",
    isUser: false
  },
  {
    id: 2,
    agent: "User",
    message: "What's the risk profile comparison between these two properties?",
    timestamp: "1 min ago", 
    isUser: true
  },
  {
    id: 3,
    agent: "Atelius",
    message: "Legal analysis complete: Oak Street has clean title with no liens. Maple Ave has 2 minor code violations that could cost ~$15K to resolve. Overall legal risk remains low for both properties.",
    timestamp: "45s ago",
    isUser: false
  },
  {
    id: 4,
    agent: "Osiris",
    message: "Financial projections updated: Oak Street shows 11.2% cash-on-cash return with 18-month break-even. Maple Ave projects 9.8% return with 22-month break-even due to renovation costs.",
    timestamp: "30s ago",
    isUser: false
  },
  {
    id: 5,
    agent: "Valyria",
    message: "Market forecast indicates Brooklyn Heights rental demand will increase 12% over next 24 months. Both properties are well-positioned for appreciation.",
    timestamp: "15s ago",
    isUser: false
  }
];

export function AIAgentChat() {
  const [selectedAgent, setSelectedAgent] = useState<string>("Eden");
  const [message, setMessage] = useState("");
  const [conversations, setConversations] = useState(mockConversations);
  const [isOpen, setIsOpen] = useState(false);

  const handleSendMessage = () => {
    if (!message.trim()) return;

    const newMessage = {
      id: conversations.length + 1,
      agent: "User",
      message: message,
      timestamp: "Just now",
      isUser: true
    };

    setConversations(prev => [...prev, newMessage]);
    setMessage("");

    // Simulate agent response
    setTimeout(() => {
      const agentProfile = agentProfiles[selectedAgent as keyof typeof agentProfiles];
      const responses = [
        `Based on my ${agentProfile.specialty.toLowerCase()}, I've completed the analysis. Here are the key findings...`,
        `I'll cross-reference this with my specialized data. ${agentProfile.specialty} shows several important factors...`,
        `My analysis using ${agentProfile.specialty.toLowerCase()} indicates strong potential. Let me break down the details...`,
        `I've processed this through my algorithms. As your ${agentProfile.role.toLowerCase()}, I recommend the following approach...`,
        `Data analysis complete. ${agentProfile.specialty} reveals some interesting insights about this opportunity...`
      ];
      
      const agentResponse = {
        id: conversations.length + 2,
        agent: selectedAgent,
        message: responses[Math.floor(Math.random() * responses.length)],
        timestamp: "Just now",
        isUser: false
      };

      setConversations(prev => [...prev, agentResponse]);
    }, 1500);
  };

  const selectedProfile = agentProfiles[selectedAgent as keyof typeof agentProfiles];
  const SelectedIcon = selectedProfile.icon;

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button className="fixed bottom-6 left-6 h-14 px-6 bg-gold text-gold-foreground hover:bg-gold/90 shadow-lg z-50">
          <MessageSquare className="w-5 h-5 mr-2" />
          Ask Janus AI
        </Button>
      </DialogTrigger>

      <DialogContent className="max-w-4xl h-[85vh] bg-card border-border p-0 flex flex-col">
        <div className="flex h-full min-h-0">
          {/* Agent Selection Sidebar */}
          <div className="w-80 bg-secondary border-r border-border flex flex-col">
            <DialogHeader className="p-4 border-b border-border shrink-0">
              <DialogTitle className="flex items-center gap-2 text-foreground">
                <Bot className="w-5 h-5 text-ice" />
                Janus AI Agents
              </DialogTitle>
            </DialogHeader>

            <ScrollArea className="flex-1 p-4">
              <div className="space-y-2">
                {Object.entries(agentProfiles).map(([name, profile]) => {
                  const IconComponent = profile.icon;
                  return (
                    <Button
                      key={name}
                      variant={selectedAgent === name ? "default" : "ghost"}
                      className={`w-full justify-start p-3 h-auto ${
                        selectedAgent === name 
                          ? 'bg-ice text-ice-foreground' 
                          : 'hover:bg-muted'
                      }`}
                      onClick={() => setSelectedAgent(name)}
                    >
                      <div className="flex items-center gap-3 w-full">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${profile.bgColor}`}>
                          <IconComponent className={`w-4 h-4 ${profile.color}`} />
                        </div>
                        <div className="text-left flex-1 min-w-0">
                          <p className="font-medium truncate">{name}</p>
                          <p className="text-xs opacity-75 truncate">{profile.role}</p>
                        </div>
                      </div>
                    </Button>
                  );
                })}
              </div>
            </ScrollArea>
          </div>

          {/* Chat Interface */}
          <div className="flex-1 flex flex-col min-h-0">
            {/* Chat Header */}
            <div className="p-4 border-b border-border bg-card shrink-0">
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center ${selectedProfile.bgColor}`}>
                  <SelectedIcon className={`w-5 h-5 ${selectedProfile.color}`} />
                </div>
                <div>
                  <h3 className="font-display text-lg font-semibold text-foreground">{selectedAgent}</h3>
                  <p className="text-sm text-muted-foreground">{selectedProfile.specialty}</p>
                </div>
                <div className="ml-auto">
                  <Badge variant="outline" className="border-success text-success">
                    Online
                  </Badge>
                </div>
              </div>
            </div>

            {/* Chat Messages */}
            <div className="flex-1 min-h-0 overflow-hidden">
              <ScrollArea className="h-full">
                <div className="p-4 space-y-4">
                  {conversations.map((conv, index) => {
                    const isUser = conv.isUser;
                    const agentProfile = isUser ? null : agentProfiles[conv.agent as keyof typeof agentProfiles];
                    const AgentIcon = agentProfile?.icon;

                    return (
                      <motion.div
                        key={conv.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.3, delay: index * 0.1 }}
                        className={`flex gap-3 w-full ${isUser ? 'flex-row-reverse' : ''}`}
                      >
                        {/* Avatar */}
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-1 ${
                          isUser ? 'bg-primary' : agentProfile?.bgColor || 'bg-muted'
                        }`}>
                          {isUser ? (
                            <User className="w-4 h-4 text-primary-foreground" />
                          ) : AgentIcon ? (
                            <AgentIcon className={`w-4 h-4 ${agentProfile?.color}`} />
                          ) : (
                            <Bot className="w-4 h-4 text-muted-foreground" />
                          )}
                        </div>

                        {/* Message */}
                        <div className={`flex-1 max-w-[80%] ${isUser ? 'text-right' : ''}`}>
                          <div className={`inline-block p-3 rounded-lg ${
                            isUser 
                              ? 'bg-primary text-primary-foreground ml-auto' 
                              : 'bg-muted text-foreground'
                          }`}>
                            {!isUser && (
                              <p className="text-xs font-medium mb-1 opacity-75">{conv.agent}</p>
                            )}
                            <p className="text-sm leading-relaxed whitespace-pre-wrap break-words">{conv.message}</p>
                          </div>
                          <p className="text-xs text-muted-foreground mt-1 px-1">{conv.timestamp}</p>
                        </div>
                      </motion.div>
                    );
                  })}
                </div>
              </ScrollArea>
            </div>

            {/* Chat Input */}
            <div className="p-4 border-t border-border bg-card shrink-0">
              <div className="flex gap-3">
                <Input
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder={`Ask ${selectedAgent} anything about real estate investment...`}
                  className="flex-1 bg-input border-border"
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                />
                <Button 
                  onClick={handleSendMessage}
                  disabled={!message.trim()}
                  className="bg-ice text-ice-foreground hover:bg-ice/90"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
              
              {/* Quick Actions */}
              <div className="flex gap-2 mt-3">
                <Button size="sm" variant="outline" className="border-border hover:bg-muted text-xs">
                  Analyze this property
                </Button>
                <Button size="sm" variant="outline" className="border-border hover:bg-muted text-xs">
                  Compare markets
                </Button>
                <Button size="sm" variant="outline" className="border-border hover:bg-muted text-xs">
                  Generate report
                </Button>
              </div>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}