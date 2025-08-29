import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { 
  Activity, 
  Bot, 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  Search, 
  Calculator, 
  FileText,
  TrendingUp,
  Database,
  Shield,
  Brain,
  GitBranch,
  X,
  Wifi,
  WifiOff,
  RefreshCw
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useAgentActivity } from "@/hooks/useAgentActivity";
import { AgentActivity } from "@/lib/agentService";
import config from "@/lib/config";

const agentIcons = {
  "Eden": Brain,
  "Orion": Search,
  "Atelius": Shield,
  "Osiris": Calculator,
  "Celestia": FileText,
  "Valyria": TrendingUp,
  "Spring": CheckCircle,
  "Elysia": Database,
  "Aurora": GitBranch
};

const agentColors = {
  "Eden": "text-gold",
  "Orion": "text-ice",
  "Atelius": "text-success",
  "Osiris": "text-warning",
  "Celestia": "text-ice",
  "Valyria": "text-gold",
  "Spring": "text-success",
  "Elysia": "text-ice",
  "Aurora": "text-gold"
};

export function AgentActivityConsole() {
  const [isOpen, setIsOpen] = useState(false);
  const { 
    activities, 
    agentsStatus, 
    loading, 
    error, 
    refreshActivities, 
    dismissActivity, 
    isBackendConnected 
  } = useAgentActivity(); // Use default polling interval from config
  
  const activeActivities = activities.filter(a => a.status === 'in-progress').length;
  const recentAlerts = activities.filter(a => a.status === 'alert').length;

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'in-progress':
        return <Clock className="w-4 h-4 text-ice animate-pulse" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-success" />;
      case 'alert':
        return <AlertCircle className="w-4 h-4 text-destructive" />;
      default:
        return <Bot className="w-4 h-4 text-muted-foreground" />;
    }
  };

  const handleRefresh = async () => {
    await refreshActivities();
  };

  return (
    <>
      {/* Floating Console Trigger */}
      <Sheet open={isOpen} onOpenChange={setIsOpen}>
        <SheetTrigger asChild>
          <Button
            size="lg"
            className="fixed bottom-6 right-6 h-14 w-14 rounded-full bg-ice text-ice-foreground hover:bg-ice/90 shadow-lg z-50"
          >
            <div className="relative">
              <Activity className="w-6 h-6" />
              {(activeActivities > 0 || recentAlerts > 0) && (
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="absolute -top-2 -right-2 h-5 w-5 bg-gold rounded-full flex items-center justify-center"
                >
                  <span className="text-xs font-bold text-gold-foreground">
                    {activeActivities + recentAlerts}
                  </span>
                </motion.div>
              )}
              {/* Connection status indicator */}
              <div className="absolute -bottom-1 -right-1">
                {isBackendConnected ? (
                  <Wifi className="w-3 h-3 text-success" />
                ) : (
                  <WifiOff className="w-3 h-3 text-destructive" />
                )}
              </div>
            </div>
          </Button>
        </SheetTrigger>

        <SheetContent className="w-96 bg-card border-l border-border flex flex-col">
          <SheetHeader className="shrink-0">
            <SheetTitle className="flex items-center gap-2 text-foreground">
              <Bot className="w-5 h-5 text-ice" />
              Agent Activity Console
              {!isBackendConnected && (
                <Badge variant="destructive" className="text-xs">
                  Offline
                </Badge>
              )}
            </SheetTitle>
          </SheetHeader>

          <div className="flex-1 flex flex-col min-h-0 mt-6">
            {/* Connection Status and Refresh */}
            <div className="flex items-center justify-between mb-4 shrink-0">
              <div className="flex items-center gap-2">
                {isBackendConnected ? (
                  <div className="flex items-center gap-1 text-xs text-success">
                    <Wifi className="w-3 h-3" />
                    Connected
                  </div>
                ) : (
                  <div className="flex items-center gap-1 text-xs text-destructive">
                    <WifiOff className="w-3 h-3" />
                    Disconnected
                  </div>
                )}
              </div>
              <Button
                size="sm"
                variant="outline"
                onClick={handleRefresh}
                disabled={loading || !isBackendConnected}
                className="h-7 px-2"
              >
                <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
              </Button>
            </div>

            {/* Activity Summary */}
            <div className="grid grid-cols-2 gap-3 mb-6 shrink-0">
              <Card className="bg-secondary border-border">
                <CardContent className="p-3 text-center">
                  <div className="text-lg font-bold text-ice">{activeActivities}</div>
                  <div className="text-xs text-muted-foreground">Active Tasks</div>
                </CardContent>
              </Card>
              <Card className="bg-secondary border-border">
                <CardContent className="p-3 text-center">
                  <div className="text-lg font-bold text-gold">{activities.filter(a => a.status === 'completed').length}</div>
                  <div className="text-xs text-muted-foreground">Completed</div>
                </CardContent>
              </Card>
            </div>

            {/* Error Display */}
            {error && (
              <div className="mb-4 p-3 bg-destructive/10 border border-destructive/20 rounded-md">
                <p className="text-sm text-destructive">{error}</p>
              </div>
            )}

            {/* Loading State */}
            {loading && (
              <div className="flex items-center justify-center py-8">
                <RefreshCw className="w-6 h-6 animate-spin text-muted-foreground" />
                <span className="ml-2 text-sm text-muted-foreground">Loading activities...</span>
              </div>
            )}

            {/* Activity Feed */}
            {!loading && (
              <div className="flex-1 min-h-0 overflow-hidden">
                <ScrollArea className="h-full">
                  <div className="space-y-3 pr-2">
                    {activities.length === 0 ? (
                      <div className="text-center py-8 text-muted-foreground">
                        <Bot className="w-8 h-8 mx-auto mb-2 opacity-50" />
                        <p className="text-sm">No activities to display</p>
                        {!isBackendConnected && (
                          <p className="text-xs mt-1">Check your backend connection</p>
                        )}
                      </div>
                    ) : (
                      <AnimatePresence>
                        {activities.map((activity, index) => {
                          const IconComponent = agentIcons[activity.agent as keyof typeof agentIcons];
                          const agentColor = agentColors[activity.agent as keyof typeof agentColors];
                          
                          return (
                            <motion.div
                              key={activity.id}
                              initial={{ opacity: 0, x: 20 }}
                              animate={{ opacity: 1, x: 0 }}
                              exit={{ opacity: 0, x: -20 }}
                              transition={{ duration: 0.3, delay: index * 0.05 }}
                            >
                              <Card className="bg-secondary/50 border-border hover:bg-secondary transition-colors relative">
                                <CardContent className="p-3">
                                  <div className="flex items-start gap-3">
                                    {/* Agent Avatar */}
                                    <div className="w-8 h-8 bg-background rounded-full flex items-center justify-center shrink-0 border border-border">
                                      {IconComponent && <IconComponent className={`w-4 h-4 ${agentColor}`} />}
                                    </div>
                                    
                                    {/* Activity Content */}
                                    <div className="flex-1 min-w-0">
                                      <div className="flex items-center gap-2 mb-1">
                                        <span className="font-medium text-foreground text-sm truncate">
                                          {activity.agent}
                                        </span>
                                        {getStatusIcon(activity.status)}
                                        <span className="text-xs text-muted-foreground ml-auto shrink-0">
                                          {activity.timestamp}
                                        </span>
                                      </div>
                                      
                                      <p className="text-sm text-foreground mb-2 leading-relaxed">
                                        {activity.message}
                                      </p>
                                      
                                      <p className="text-xs text-muted-foreground leading-relaxed">
                                        {activity.details}
                                      </p>
                                      
                                      {activity.status === 'in-progress' && (
                                        <div className="mt-3">
                                          <div className="w-full bg-muted rounded-full h-1.5">
                                            <motion.div
                                              className="bg-ice h-1.5 rounded-full"
                                              initial={{ width: "0%" }}
                                              animate={{ width: "75%" }}
                                              transition={{ duration: 2, repeat: Infinity, repeatType: "reverse" }}
                                            />
                                          </div>
                                        </div>
                                      )}
                                    </div>
                                    
                                    {/* Dismiss Button */}
                                    {(activity.status === 'alert' || activity.status === 'completed') && (
                                      <Button
                                        size="sm"
                                        variant="ghost"
                                        className="w-6 h-6 p-0 shrink-0 opacity-50 hover:opacity-100"
                                        onClick={() => dismissActivity(activity.id)}
                                        disabled={!isBackendConnected}
                                      >
                                        <X className="w-3 h-3" />
                                      </Button>
                                    )}
                                  </div>
                                </CardContent>
                              </Card>
                            </motion.div>
                          );
                        })}
                      </AnimatePresence>
                    )}
                  </div>
                </ScrollArea>
              </div>
            )}

            {/* Console Actions */}
            <div className="pt-4 border-t border-border shrink-0">
              <div className="flex gap-2">
                <Button 
                  size="sm" 
                  variant="outline" 
                  className="flex-1 border-border hover:bg-muted"
                  disabled={!isBackendConnected}
                >
                  <Bot className="w-4 h-4 mr-2" />
                  Agent Settings
                </Button>
                <Button 
                  size="sm" 
                  variant="outline" 
                  className="flex-1 border-border hover:bg-muted"
                  disabled={!isBackendConnected}
                >
                  <Activity className="w-4 h-4 mr-2" />
                  View Logs
                </Button>
              </div>
            </div>
          </div>
        </SheetContent>
      </Sheet>
    </>
  );
}