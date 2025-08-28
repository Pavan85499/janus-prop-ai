import { NavLink, useLocation } from "react-router-dom";
import { 
  LayoutDashboard, 
  Bot, 
  Building2, 
  Briefcase, 
  Handshake,
  Activity,
  Settings,
  Zap
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
];

const tools = [
  { name: "Analytics", href: "/analytics", icon: Activity },
  { name: "Automations", href: "/automations", icon: Zap },
  { name: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const { state } = useSidebar();
  const location = useLocation();
  const collapsed = state === "collapsed";

  const isActive = (path: string) => location.pathname === path;

  return (
    <ShadcnSidebar className={`border-r border-border/50 bg-card/30 backdrop-blur-lg ${collapsed ? "w-16" : "w-64"}`}>
      <SidebarContent className="pt-8">
        {/* Logo */}
        <div className="px-6 mb-8">
          {!collapsed && (
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center glow-primary">
                <Bot className="w-5 h-5 text-primary-foreground" />
              </div>
              <h1 className="font-display text-xl font-normal">Janus AI</h1>
            </div>
          )}
          {collapsed && (
            <div className="flex justify-center">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center glow-primary">
                <Bot className="w-5 h-5 text-primary-foreground" />
              </div>
            </div>
          )}
        </div>

        {/* Navigation */}
        <SidebarGroup>
          <SidebarGroupLabel className={collapsed ? "sr-only" : ""}>
            Navigation
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {navigation.map((item) => (
                <SidebarMenuItem key={item.name}>
                  <SidebarMenuButton asChild>
                    <NavLink
                      to={item.href}
                      className={({ isActive }) =>
                        `flex items-center gap-3 px-3 py-2 rounded-lg transition-all duration-200 ${
                          isActive
                            ? "bg-primary/20 text-primary border border-primary/30"
                            : "text-muted-foreground hover:text-foreground hover:bg-secondary/50"
                        }`
                      }
                    >
                      <item.icon className="w-5 h-5 shrink-0" />
                      {!collapsed && <span className="font-medium">{item.name}</span>}
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {/* Tools */}
        <SidebarGroup>
          <SidebarGroupLabel className={collapsed ? "sr-only" : ""}>
            Tools
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {tools.map((item) => (
                <SidebarMenuItem key={item.name}>
                  <SidebarMenuButton asChild>
                    <NavLink
                      to={item.href}
                      className={({ isActive }) =>
                        `flex items-center gap-3 px-3 py-2 rounded-lg transition-all duration-200 ${
                          isActive
                            ? "bg-primary/20 text-primary border border-primary/30"
                            : "text-muted-foreground hover:text-foreground hover:bg-secondary/50"
                        }`
                      }
                    >
                      <item.icon className="w-5 h-5 shrink-0" />
                      {!collapsed && <span className="font-medium">{item.name}</span>}
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