import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  Bot, 
  Play, 
  Pause, 
  Settings, 
  Clock, 
  Zap, 
  Workflow, 
  AlertCircle, 
  CheckCircle, 
  Plus,
  Edit,
  Trash2,
  PlayCircle
} from 'lucide-react';
import { AppLayout } from '@/components/layout/AppLayout';

interface Workflow {
  id: number;
  name: string;
  description: string;
  status: string;
  triggers: string[];
  actions: string[];
  lastRun: string;
  nextRun: string;
}

const Automation = () => {
  const [workflows, setWorkflows] = useState([
    {
      id: 1,
      name: 'Lead Qualification',
      description: 'Automatically qualify leads based on investment criteria',
      status: 'active',
      triggers: ['New lead added', 'Property inquiry'],
      actions: ['Send welcome email', 'Assign to agent', 'Create task'],
      lastRun: '2 hours ago',
      nextRun: 'In 4 hours'
    },
    {
      id: 2,
      name: 'Market Analysis',
      description: 'Generate market reports for new properties',
      status: 'paused',
      triggers: ['Property added', 'Weekly schedule'],
      actions: ['Run market analysis', 'Update property data', 'Notify team'],
      lastRun: '1 day ago',
      nextRun: 'Paused'
    },
    {
      id: 3,
      name: 'Deal Follow-up',
      description: 'Send follow-up emails and reminders for active deals',
      status: 'active',
      triggers: ['Deal created', 'Deal updated'],
      actions: ['Send follow-up email', 'Create reminder', 'Update status'],
      lastRun: '30 minutes ago',
      nextRun: 'In 2 hours'
    }
  ]);

  const [templates, setTemplates] = useState([
    {
      id: 1,
      name: 'Property Analysis Template',
      type: 'Analysis',
      description: 'Comprehensive property analysis workflow',
      usage: 45,
      lastUsed: '2 days ago'
    },
    {
      id: 2,
      name: 'Lead Nurturing Sequence',
      type: 'Marketing',
      description: 'Automated lead nurturing email sequence',
      usage: 23,
      lastUsed: '1 week ago'
    },
    {
      id: 3,
      name: 'Deal Pipeline Update',
      type: 'Management',
      description: 'Automated deal status updates and notifications',
      usage: 67,
      lastUsed: '1 day ago'
    }
  ]);

  const [isCreatingWorkflow, setIsCreatingWorkflow] = useState(false);
  const [newWorkflow, setNewWorkflow] = useState({
    name: '',
    description: '',
    trigger: '',
    action: ''
  });

  const toggleWorkflow = (id: number) => {
    setWorkflows(workflows.map(workflow => 
      workflow.id === id 
        ? { ...workflow, status: workflow.status === 'active' ? 'paused' : 'active' }
        : workflow
    ));
  };

  const createWorkflow = () => {
    if (newWorkflow.name && newWorkflow.description) {
      const workflow = {
        id: workflows.length + 1,
        name: newWorkflow.name,
        description: newWorkflow.description,
        status: 'active',
        triggers: [newWorkflow.trigger],
        actions: [newWorkflow.action],
        lastRun: 'Never',
        nextRun: 'Pending'
      };
      setWorkflows([...workflows, workflow]);
      setNewWorkflow({ name: '', description: '', trigger: '', action: '' });
      setIsCreatingWorkflow(false);
    }
  };

  const WorkflowCard = ({ workflow }: { workflow: Workflow }) => (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Workflow className="h-5 w-5" />
              {workflow.name}
            </CardTitle>
            <CardDescription>{workflow.description}</CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Switch
              checked={workflow.status === 'active'}
              onCheckedChange={() => toggleWorkflow(workflow.id)}
            />
            <Badge variant={workflow.status === 'active' ? 'default' : 'secondary'}>
              {workflow.status}
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div>
            <h4 className="text-sm font-medium mb-2">Triggers</h4>
            <div className="flex flex-wrap gap-1">
              {workflow.triggers.map((trigger: string, index: number) => (
                <Badge key={index} variant="outline" className="text-xs">
                  {trigger}
                </Badge>
              ))}
            </div>
          </div>
          <div>
            <h4 className="text-sm font-medium mb-2">Actions</h4>
            <div className="flex flex-wrap gap-1">
              {workflow.actions.map((action: string, index: number) => (
                <Badge key={index} variant="outline" className="text-xs">
                  {action}
                </Badge>
              ))}
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-muted-foreground">Last Run:</span>
              <p className="font-medium">{workflow.lastRun}</p>
            </div>
            <div>
              <span className="text-muted-foreground">Next Run:</span>
              <p className="font-medium">{workflow.nextRun}</p>
            </div>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm">
              <Edit className="h-4 w-4 mr-1" />
              Edit
            </Button>
            <Button variant="outline" size="sm">
              <PlayCircle className="h-4 w-4 mr-1" />
              Run Now
            </Button>
            <Button variant="outline" size="sm" className="text-red-600 hover:text-red-700">
              <Trash2 className="h-4 w-4 mr-1" />
              Delete
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <AppLayout>
      <div className="flex-1 space-y-6 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Automation</h2>
          <p className="text-muted-foreground">
            Streamline your real estate operations with intelligent workflows
          </p>
        </div>
        <Button onClick={() => setIsCreatingWorkflow(true)}>
          <Plus className="mr-2 h-4 w-4" />
          Create Workflow
        </Button>
      </div>

      <Tabs defaultValue="workflows" className="space-y-4">
        <TabsList>
          <TabsTrigger value="workflows">Workflows</TabsTrigger>
          <TabsTrigger value="templates">Templates</TabsTrigger>
          <TabsTrigger value="logs">Execution Logs</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        <TabsContent value="workflows" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {workflows.map((workflow) => (
              <WorkflowCard key={workflow.id} workflow={workflow} />
            ))}
          </div>

          {isCreatingWorkflow && (
            <Card>
              <CardHeader>
                <CardTitle>Create New Workflow</CardTitle>
                <CardDescription>Set up a new automation workflow</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <Label htmlFor="workflow-name">Workflow Name</Label>
                    <Input
                      id="workflow-name"
                      value={newWorkflow.name}
                      onChange={(e) => setNewWorkflow({...newWorkflow, name: e.target.value})}
                      placeholder="Enter workflow name"
                    />
                  </div>
                  <div>
                    <Label htmlFor="trigger">Trigger</Label>
                    <Select value={newWorkflow.trigger} onValueChange={(value) => setNewWorkflow({...newWorkflow, trigger: value})}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select trigger" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="New lead added">New lead added</SelectItem>
                        <SelectItem value="Property added">Property added</SelectItem>
                        <SelectItem value="Deal created">Deal created</SelectItem>
                        <SelectItem value="Scheduled">Scheduled</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div>
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    value={newWorkflow.description}
                    onChange={(e) => setNewWorkflow({...newWorkflow, description: e.target.value})}
                    placeholder="Describe what this workflow does"
                  />
                </div>
                <div>
                  <Label htmlFor="action">Action</Label>
                  <Select value={newWorkflow.action} onValueChange={(value) => setNewWorkflow({...newWorkflow, action: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select action" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Send email">Send email</SelectItem>
                      <SelectItem value="Create task">Create task</SelectItem>
                      <SelectItem value="Update status">Update status</SelectItem>
                      <SelectItem value="Notify team">Notify team</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex gap-2">
                  <Button onClick={createWorkflow}>Create Workflow</Button>
                  <Button variant="outline" onClick={() => setIsCreatingWorkflow(false)}>
                    Cancel
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="templates" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {templates.map((template) => (
              <Card key={template.id}>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Bot className="h-5 w-5" />
                    {template.name}
                  </CardTitle>
                  <CardDescription>{template.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Type:</span>
                      <Badge variant="outline">{template.type}</Badge>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Usage:</span>
                      <span className="font-medium">{template.usage} times</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Last Used:</span>
                      <span className="font-medium">{template.lastUsed}</span>
                    </div>
                  </div>
                  <div className="flex gap-2 mt-4">
                    <Button variant="outline" size="sm" className="flex-1">
                      <Play className="h-4 w-4 mr-1" />
                      Use Template
                    </Button>
                    <Button variant="outline" size="sm">
                      <Edit className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="logs" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Execution Logs</CardTitle>
              <CardDescription>Recent workflow executions and their results</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  { workflow: 'Lead Qualification', status: 'success', time: '2 hours ago', duration: '45s' },
                  { workflow: 'Market Analysis', status: 'success', time: '4 hours ago', duration: '2m 15s' },
                  { workflow: 'Deal Follow-up', status: 'error', time: '6 hours ago', duration: '12s' },
                  { workflow: 'Lead Qualification', status: 'success', time: '8 hours ago', duration: '38s' },
                  { workflow: 'Market Analysis', status: 'success', time: '1 day ago', duration: '1m 52s' }
                ].map((log, index) => (
                  <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-3">
                      {log.status === 'success' ? (
                        <CheckCircle className="h-5 w-5 text-green-500" />
                      ) : (
                        <AlertCircle className="h-5 w-5 text-red-500" />
                      )}
                      <div>
                        <p className="font-medium">{log.workflow}</p>
                        <p className="text-sm text-muted-foreground">{log.time}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge variant={log.status === 'success' ? 'default' : 'destructive'}>
                        {log.status}
                      </Badge>
                      <p className="text-sm text-muted-foreground mt-1">{log.duration}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="settings" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Automation Settings</CardTitle>
              <CardDescription>Configure global automation preferences</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-medium">Enable Automation</h4>
                  <p className="text-sm text-muted-foreground">Allow workflows to run automatically</p>
                </div>
                <Switch defaultChecked />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-medium">Email Notifications</h4>
                  <p className="text-sm text-muted-foreground">Get notified when workflows complete</p>
                </div>
                <Switch defaultChecked />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-medium">Error Alerts</h4>
                  <p className="text-sm text-muted-foreground">Receive alerts when workflows fail</p>
                </div>
                <Switch defaultChecked />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-medium">Execution Logs</h4>
                  <p className="text-sm text-muted-foreground">Keep detailed logs of all executions</p>
                </div>
                <Switch defaultChecked />
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
      </div>
    </AppLayout>
  );
};

export default Automation;
