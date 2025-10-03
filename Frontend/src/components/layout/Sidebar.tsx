import { NavLink, useLocation } from "react-router-dom";
import { 
  LayoutDashboard, 
  Bot, 
  Building2, 
  Briefcase, 
  Handshake,
  Activity,
  Settings,
  Zap,
  Search,
  FileText,
  Calculator,
  Shield,
  Users,
  TrendingUp,
  CreditCard
} from "lucide-react";
import {
  Sidebar as ShadcnSidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar";

const navigation = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Agents", href: "/agents", icon: Bot },
  { name: "Properties", href: "/properties", icon: Building2 },
  { name: "Portfolios", href: "/portfolios", icon: Briefcase },
  { name: "Deal Room", href: "/deals", icon: Handshake },
  { name: "Property Scanner", href: "/property-scanner", icon: Search },
];

const aiFeatures = [
  { name: "Document Management", href: "/documents", icon: FileText },
  { name: "Underwriting", href: "/underwriting", icon: Calculator },
  { name: "Legal & Compliance", href: "/legal-compliance", icon: Shield },
  { name: "AI Investment Committee", href: "/investment-committee", icon: Users },
];

const execution = [
  { name: "Execution & Closing", href: "/execution-closing", icon: Handshake },
  { name: "Post-Acquisition", href: "/post-acquisition", icon: TrendingUp },
];

const tools = [
  { name: "Analytics", href: "/analytics", icon: Activity },
  { name: "Automation", href: "/automation", icon: Zap },
  { name: "Subscription", href: "/subscription", icon: CreditCard },
  { name: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const { state } = useSidebar();
  const location = useLocation();
  const collapsed = state === "collapsed";

  const isActive = (path: string) => location.pathname === path;

  return (
    <ShadcnSidebar className={`
      border-r border-border/50 bg-card/30 backdrop-blur-lg 
      transition-all duration-300 ease-out
      ${collapsed ? "w-16" : "w-64"}
    `}>
      <SidebarContent className="pt-6 sm:pt-8">
        {/* Logo */}
        <div className="px-4 sm:px-6 mb-6 sm:mb-8">
          {!collapsed && (
            <div className="flex items-center gap-3 responsive-fade-in">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center 
                           animate-glow hover:animate-wiggle transition-all duration-300">
                <Bot className="w-5 h-5 text-primary-foreground" />
              </div>
              <h1 className="font-display text-xl font-normal animatic-heading">
                Janus AI
              </h1>
            </div>
          )}
          {collapsed && (
            <div className="flex justify-center">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center 
                           animate-glow hover:animate-wiggle transition-all duration-300">
                <Bot className="w-5 h-5 text-primary-foreground" />
              </div>
            </div>
          )}
        </div>

        {/* Navigation */}
        <SidebarGroup>
          <SidebarGroupLabel className={`text-xs font-semibold text-muted-foreground uppercase tracking-wider 
                                        ${collapsed ? "sr-only" : "px-4 sm:px-6 mb-2"}`}>
            Navigation
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu className="space-y-1">
              {navigation.map((item, index) => (
                <SidebarMenuItem key={item.name}>
                  <SidebarMenuButton asChild>
                    <NavLink
                      to={item.href}
                      className={({ isActive }) =>
                        `group flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-300 
                         hover:scale-105 focus-ring relative overflow-hidden
                         ${isActive
                            ? "bg-primary/20 text-primary border border-primary/30 shadow-lg shadow-primary/10"
                            : "text-muted-foreground hover:text-foreground hover:bg-secondary/50"
                         }`
                      }
                      style={{ animationDelay: `${index * 100}ms` }}
                    >
                      <item.icon className={`w-5 h-5 shrink-0 transition-all duration-300 
                                            ${isActive ? 'animate-pulse' : 'group-hover:scale-110'}`} />
                      {!collapsed && (
                        <span className="font-medium animatic-text transition-all duration-300">
                          {item.name}
                        </span>
                      )}
                      {isActive && (
                        <div className="absolute inset-0 bg-gradient-to-r from-primary/10 to-transparent 
                                      animate-shimmer"></div>
                      )}
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {/* AI Features */}
        <SidebarGroup>
          <SidebarGroupLabel className={`text-xs font-semibold text-muted-foreground uppercase tracking-wider 
                                        ${collapsed ? "sr-only" : "px-4 sm:px-6 mb-2"}`}>
            AI Features
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu className="space-y-1">
              {aiFeatures.map((item, index) => (
                <SidebarMenuItem key={item.name}>
                  <SidebarMenuButton asChild>
                    <NavLink
                      to={item.href}
                      className={({ isActive }) =>
                        `group flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-300 
                         hover:scale-105 focus-ring relative overflow-hidden
                         ${isActive
                            ? "bg-primary/20 text-primary border border-primary/30 shadow-lg shadow-primary/10"
                            : "text-muted-foreground hover:text-foreground hover:bg-secondary/50"
                         }`
                      }
                      style={{ animationDelay: `${(index + navigation.length) * 100}ms` }}
                    >
                      <item.icon className={`w-5 h-5 shrink-0 transition-all duration-300 
                                            ${isActive ? 'animate-pulse' : 'group-hover:scale-110'}`} />
                      {!collapsed && (
                        <span className="font-medium animatic-text transition-all duration-300">
                          {item.name}
                        </span>
                      )}
                      {isActive && (
                        <div className="absolute inset-0 bg-gradient-to-r from-primary/10 to-transparent 
                                      animate-shimmer"></div>
                      )}
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {/* Execution */}
        <SidebarGroup>
          <SidebarGroupLabel className={`text-xs font-semibold text-muted-foreground uppercase tracking-wider 
                                        ${collapsed ? "sr-only" : "px-4 sm:px-6 mb-2"}`}>
            Execution
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu className="space-y-1">
              {execution.map((item, index) => (
                <SidebarMenuItem key={item.name}>
                  <SidebarMenuButton asChild>
                    <NavLink
                      to={item.href}
                      className={({ isActive }) =>
                        `group flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-300 
                         hover:scale-105 focus-ring relative overflow-hidden
                         ${isActive
                            ? "bg-primary/20 text-primary border border-primary/30 shadow-lg shadow-primary/10"
                            : "text-muted-foreground hover:text-foreground hover:bg-secondary/50"
                         }`
                      }
                      style={{ animationDelay: `${(index + navigation.length + aiFeatures.length) * 100}ms` }}
                    >
                      <item.icon className={`w-5 h-5 shrink-0 transition-all duration-300 
                                            ${isActive ? 'animate-pulse' : 'group-hover:scale-110'}`} />
                      {!collapsed && (
                        <span className="font-medium animatic-text transition-all duration-300">
                          {item.name}
                        </span>
                      )}
                      {isActive && (
                        <div className="absolute inset-0 bg-gradient-to-r from-primary/10 to-transparent 
                                      animate-shimmer"></div>
                      )}
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {/* Tools */}
        <SidebarGroup>
          <SidebarGroupLabel className={`text-xs font-semibold text-muted-foreground uppercase tracking-wider 
                                        ${collapsed ? "sr-only" : "px-4 sm:px-6 mb-2"}`}>
            Tools
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu className="space-y-1">
              {tools.map((item, index) => (
                <SidebarMenuItem key={item.name}>
                  <SidebarMenuButton asChild>
                    <NavLink
                      to={item.href}
                      className={({ isActive }) =>
                        `group flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-300 
                         hover:scale-105 focus-ring relative overflow-hidden
                         ${isActive
                            ? "bg-primary/20 text-primary border border-primary/30 shadow-lg shadow-primary/10"
                            : "text-muted-foreground hover:text-foreground hover:bg-secondary/50"
                         }`
                      }
                      style={{ animationDelay: `${(index + navigation.length + aiFeatures.length + execution.length) * 100}ms` }}
                    >
                      <item.icon className={`w-5 h-5 shrink-0 transition-all duration-300 
                                            ${isActive ? 'animate-pulse' : 'group-hover:scale-110'}`} />
                      {!collapsed && (
                        <span className="font-medium animatic-text transition-all duration-300">
                          {item.name}
                        </span>
                      )}
                      {isActive && (
                        <div className="absolute inset-0 bg-gradient-to-r from-primary/10 to-transparent 
                                      animate-shimmer"></div>
                      )}
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </ShadcnSidebar>
  );
}