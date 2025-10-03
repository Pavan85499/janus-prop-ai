import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { 
  Plus, 
  Bot, 
  Play, 
  Pause, 
  Settings, 
  Activity, 
  Zap,
  Brain,
  Search,
  Filter,
  RefreshCw,
  Trash2,
  Edit
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { AppLayout } from "@/components/layout/AppLayout";
import config from "@/lib/config";
import agentService from "@/lib/agentService";

interface Agent {
  id: string;
  name: string;
  type: string;
  status: 'active' | 'inactive' | 'error';
  description: string;
  capabilities: string[];
  last_activity: string;
  tasks_completed: number;
  success_rate: number;
  created_at: string;
  updated_at: string;
}

interface AgentTask {
  id: string;
  agent_id: string;
  task_type: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  description: string;
  created_at: string;
  completed_at?: string;
  result?: unknown;
}

const AGENT_TYPES = [
  { value: "property_analyzer", label: "Property Analyzer", description: "Analyzes property data and market trends" },
  { value: "lead_generator", label: "Lead Generator", description: "Identifies and qualifies potential leads" },
  { value: "market_researcher", label: "Market Researcher", description: "Researches market conditions and opportunities" },
  { value: "investment_advisor", label: "Investment Advisor", description: "Provides investment recommendations" },
  { value: "data_collector", label: "Data Collector", description: "Collects and processes real estate data" },
  { value: "custom", label: "Custom Agent", description: "Custom agent with specific capabilities" },
];

const TASK_TYPES = [
  "property_analysis",
  "lead_generation", 
  "market_research",
  "investment_analysis",
  "data_collection",
  "report_generation"
];

export default function Agents() {
  const { toast } = useToast();
  
  const [agents, setAgents] = useState<Agent[]>([]);
  const [tasks, setTasks] = useState<AgentTask[]>([]);
  const [loading, setLoading] = useState(false);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  
  const [newAgent, setNewAgent] = useState({
    name: "",
    type: "",
    description: "",
    capabilities: [] as string[],
  });

  // Load agents and tasks
  useEffect(() => {
    loadAgents();
    loadTasks();
    const interval = setInterval(() => {
      loadAgents();
      loadTasks();
    }, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadAgents = async () => {
    try {
      setLoading(true);
      const data = await agentService.getAgentsStatus();
      // data.agents is expected to be an array per backend
      const list = Array.isArray((data as any).agents) ? (data as any).agents : [];
      const agentList: Agent[] = list.map((agentData: any) => ({
        id: agentData.agent_id || agentData.name || crypto.randomUUID(),
        name: agentData.name || agentData.agent_id || "Agent",
        type: "property_analyzer",
        status: agentData.status === "online" || agentData.status === "running" ? "active" : agentData.status === "error" ? "error" : "inactive",
        description: `AI agent for ${agentData.name || agentData.agent_id} operations`,
        capabilities: agentData.capabilities || ["property_analysis", "data_processing"],
        last_activity: agentData.last_activity || new Date().toISOString(),
        tasks_completed: agentData.performance_metrics?.tasks_completed || agentData.tasks_completed || 0,
        success_rate: Math.round((agentData.performance_metrics?.accuracy || 0.9) * 100),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }));
      setAgents(agentList);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load agents",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const loadTasks = async () => {
    try {
      const data = await agentService.getAgentActivity(50);
      setTasks((data as any).activities || []);
    } catch (error) {
      console.error("Failed to load tasks:", error);
    }
  };

  const createAgent = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${config.api.baseUrl}/api/v1/agents`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newAgent),
      });

      if (response.ok) {
        toast({
          title: "Success",
          description: "Agent created successfully",
        });
        setShowCreateDialog(false);
        setNewAgent({ name: "", type: "", description: "", capabilities: [] });
        loadAgents();
      } else {
        toast({
          title: "Error",
          description: "Failed to create agent",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create agent",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const startAgent = async (agentId: string) => {
    try {
      const response = await fetch(`${config.api.baseUrl}/api/v1/agents/${agentId}/start`, {
        method: 'POST',
      });

      if (response.ok) {
        toast({
          title: "Success",
          description: "Agent started successfully",
        });
        loadAgents();
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to start agent",
        variant: "destructive",
      });
    }
  };

  const stopAgent = async (agentId: string) => {
    try {
      const response = await fetch(`${config.api.baseUrl}/api/v1/agents/${agentId}/stop`, {
        method: 'POST',
      });

      if (response.ok) {
        toast({
          title: "Success",
          description: "Agent stopped successfully",
        });
        loadAgents();
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to stop agent",
        variant: "destructive",
      });
    }
  };

  const submitTask = async (agentId: string, taskType: string, description: string) => {
    try {
      const response = await fetch(`${config.api.baseUrl}/api/v1/agents/${agentId}/tasks`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          task_type: taskType,
          description: description,
        }),
      });

      if (response.ok) {
        toast({
          title: "Success",
          description: "Task submitted successfully",
        });
        loadTasks();
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to submit task",
        variant: "destructive",
      });
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-success/20 text-success border-success/30';
      case 'inactive': return 'bg-muted/20 text-muted-foreground border-muted/30';
      case 'error': return 'bg-destructive/20 text-destructive border-destructive/30';
      default: return 'bg-muted/20 text-muted-foreground border-muted/30';
    }
  };

  const filteredAgents = agents.filter(agent => {
    const matchesSearch = agent.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         agent.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === "all" || agent.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <AppLayout>
      <div className="min-h-screen bg-gradient-to-br from-background to-muted">
      {/* Header */}
      <div className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold">AI Agents</h1>
              <p className="text-muted-foreground mt-1">
                Manage and monitor your AI agents
              </p>
            </div>
            <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
              <DialogTrigger asChild>
                <Button className="flex items-center gap-2">
                  <Plus className="w-4 h-4" />
                  Create Agent
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-md">
                <DialogHeader>
                  <DialogTitle>Create New Agent</DialogTitle>
                  <DialogDescription>
                    Create a new AI agent with specific capabilities
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Agent Name</Label>
                    <Input
                      id="name"
                      value={newAgent.name}
                      onChange={(e) => setNewAgent(prev => ({ ...prev, name: e.target.value }))}
                      placeholder="Enter agent name"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="type">Agent Type</Label>
                    <Select value={newAgent.type} onValueChange={(value) => setNewAgent(prev => ({ ...prev, type: value }))}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select agent type" />
                      </SelectTrigger>
                      <SelectContent>
                        {AGENT_TYPES.map((type) => (
                          <SelectItem key={type.value} value={type.value}>
                            <div>
                              <div className="font-medium">{type.label}</div>
                              <div className="text-sm text-muted-foreground">{type.description}</div>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="description">Description</Label>
                    <Textarea
                      id="description"
                      value={newAgent.description}
                      onChange={(e) => setNewAgent(prev => ({ ...prev, description: e.target.value }))}
                      placeholder="Describe the agent's purpose and capabilities"
                      rows={3}
                    />
                  </div>
                  <div className="flex justify-end space-x-2">
                    <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                      Cancel
                    </Button>
                    <Button onClick={createAgent} disabled={loading}>
                      {loading ? "Creating..." : "Create Agent"}
                    </Button>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <Bot className="w-5 h-5 text-primary" />
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Agents</p>
                  <p className="text-2xl font-bold">{agents.length}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <Activity className="w-5 h-5 text-success" />
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Active Agents</p>
                  <p className="text-2xl font-bold">{agents.filter(a => a.status === 'active').length}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <Zap className="w-5 h-5 text-warning" />
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Tasks Completed</p>
                  <p className="text-2xl font-bold">{agents.reduce((sum, a) => sum + a.tasks_completed, 0)}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <Brain className="w-5 h-5 text-info" />
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Success Rate</p>
                  <p className="text-2xl font-bold">
                    {agents.length > 0 ? Math.round(agents.reduce((sum, a) => sum + a.success_rate, 0) / agents.length) : 0}%
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Filters */}
        <div className="flex items-center space-x-4 mb-6">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
              <Input
                placeholder="Search agents..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="Filter by status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="active">Active</SelectItem>
              <SelectItem value="inactive">Inactive</SelectItem>
              <SelectItem value="error">Error</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline" onClick={loadAgents}>
            <RefreshCw className="w-4 h-4" />
          </Button>
        </div>

        {/* Agents Table */}
        <Card>
          <CardHeader>
            <CardTitle>Agents</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                <p className="mt-2 text-muted-foreground">Loading agents...</p>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Tasks</TableHead>
                    <TableHead>Success Rate</TableHead>
                    <TableHead>Last Activity</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredAgents.map((agent) => (
                    <TableRow key={agent.id}>
                      <TableCell>
                        <div className="flex items-center space-x-2">
                          <Bot className="w-4 h-4" />
                          <span className="font-medium">{agent.name}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">
                          {AGENT_TYPES.find(t => t.value === agent.type)?.label || agent.type}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Badge className={getStatusColor(agent.status)}>
                          {agent.status}
                        </Badge>
                      </TableCell>
                      <TableCell>{agent.tasks_completed}</TableCell>
                      <TableCell>{agent.success_rate}%</TableCell>
                      <TableCell>
                        {new Date(agent.last_activity).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center space-x-2">
                          {agent.status === 'active' ? (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => stopAgent(agent.id)}
                            >
                              <Pause className="w-3 h-3" />
                            </Button>
                          ) : (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => startAgent(agent.id)}
                            >
                              <Play className="w-3 h-3" />
                            </Button>
                          )}
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => setSelectedAgent(agent)}
                          >
                            <Settings className="w-3 h-3" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        {/* Agent Details Dialog */}
        {selectedAgent && (
          <Dialog open={!!selectedAgent} onOpenChange={() => setSelectedAgent(null)}>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>{selectedAgent.name} Details</DialogTitle>
                <DialogDescription>
                  Manage and monitor this agent
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-6">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-sm font-medium text-muted-foreground">Status</Label>
                    <Badge className={getStatusColor(selectedAgent.status)}>
                      {selectedAgent.status}
                    </Badge>
                  </div>
                  <div>
                    <Label className="text-sm font-medium text-muted-foreground">Type</Label>
                    <p>{AGENT_TYPES.find(t => t.value === selectedAgent.type)?.label}</p>
                  </div>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-muted-foreground">Description</Label>
                  <p className="text-sm">{selectedAgent.description}</p>
                </div>

                <div>
                  <Label className="text-sm font-medium text-muted-foreground">Capabilities</Label>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {selectedAgent.capabilities.map((capability) => (
                      <Badge key={capability} variant="secondary">
                        {capability}
                      </Badge>
                    ))}
                  </div>
                </div>

                <div>
                  <Label className="text-sm font-medium text-muted-foreground">Submit Task</Label>
                  <div className="space-y-2 mt-2">
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select task type" />
                      </SelectTrigger>
                      <SelectContent>
                        {TASK_TYPES.map((type) => (
                          <SelectItem key={type} value={type}>
                            {type.replace('_', ' ').toUpperCase()}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <Textarea
                      placeholder="Describe the task..."
                      rows={3}
                    />
                    <Button size="sm">Submit Task</Button>
                  </div>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        )}
      </div>
      </div>
    </AppLayout>
  );
}
