import { Button } from "@/components/ui/button";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Plus, User, Settings, LogOut, MessageSquare, Bell, Search } from "lucide-react";
import { useState, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { useAskJanus } from "@/contexts/AskJanusContext";

export function Header() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [notificationCount, setNotificationCount] = useState(3);
  const { setIsOpen } = useAskJanus();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 0);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <header className={`
      relative responsive-header border-b border-border/50 bg-card/30 backdrop-blur-lg 
      flex items-center justify-between responsive-padding-x
      transition-all duration-300 ease-out
      ${isScrolled ? 'shadow-lg shadow-primary/5' : ''}
    `}>
      {/* Left Section */}
      <div className="flex items-center gap-3 sm:gap-4">
        <SidebarTrigger className="text-muted-foreground hover:text-foreground transition-colors duration-200" />
        
        {/* AI Status Indicator */}
        <div className="flex items-center gap-2 responsive-fade-in">
          <div className="w-2 h-2 bg-success rounded-full animate-ai-pulse"></div>
          <span className="text-xs sm:text-sm text-muted-foreground hidden sm:inline">
            Real-time Intelligence Active
          </span>
          <span className="text-xs text-muted-foreground sm:hidden">
            AI Active
          </span>
        </div>
      </div>

      {/* Center Section - Search */}
      <div className="flex-1 max-w-md mx-2 sm:mx-4 hidden sm:block">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
          <input
            type="text"
            placeholder="Search properties, deals..."
            className="w-full pl-10 pr-4 py-2 bg-secondary/50 border border-border/50 rounded-lg 
                     text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 
                     focus:ring-primary/50 focus:border-primary/50 transition-all duration-200
                     touch-target"
          />
        </div>
      </div>

      {/* Right Section */}
      <div className="flex items-center gap-2 sm:gap-4">
        {/* Notifications */}
        <Button 
          variant="ghost" 
          size="sm"
          className="relative p-2 hover:bg-secondary/50 transition-all duration-200"
        >
          <Bell className="w-4 h-4" />
          {notificationCount > 0 && (
            <span className="absolute -top-1 -right-1 bg-destructive text-destructive-foreground 
                           text-xs rounded-full w-5 h-5 flex items-center justify-center
                           animate-bounce">
              {notificationCount}
            </span>
          )}
        </Button>

        {/* Action Buttons */}
        <div className="hidden sm:flex items-center gap-2">
          <Button 
            variant="default" 
            size="sm" 
            className="btn-animatic bg-gradient-primary hover:bg-primary/90 
                     focus-ring transition-all duration-200 touch-target"
          >
            <Plus className="w-4 h-4 mr-2" />
            <span className="hidden lg:inline">Add Property</span>
          </Button>
          
          <Button 
            variant="outline" 
            size="sm"
            onClick={() => setIsOpen(true)}
            className="btn-animatic border-primary/30 text-primary hover:bg-primary/10 
                     focus-ring transition-all duration-200 touch-target"
          >
            <MessageSquare className="w-4 h-4 mr-2" />
            <span className="hidden lg:inline">Ask Janus</span>
          </Button>
        </div>

        {/* Mobile Action Buttons */}
        <div className="flex sm:hidden items-center gap-2">
          <Button 
            variant="ghost" 
            size="sm"
            onClick={() => setIsOpen(true)}
            className="touch-target p-2"
          >
            <MessageSquare className="w-4 h-4" />
          </Button>
          <Button 
            variant="default" 
            size="sm" 
            className="btn-animatic bg-gradient-primary hover:bg-primary/90 
                     focus-ring transition-all duration-200 touch-target"
          >
            <Plus className="w-4 h-4" />
          </Button>
        </div>

        {/* User Menu */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button 
              variant="ghost" 
              className="relative h-8 w-8 rounded-full hover:bg-secondary/50 
                       transition-all duration-200 focus-ring"
            >
              <Avatar className="h-8 w-8 ring-2 ring-primary/20 hover:ring-primary/40 
                               transition-all duration-200">
                <AvatarImage src="/placeholder.svg" alt="User" />
                <AvatarFallback className="bg-primary text-primary-foreground 
                                         animate-pulse">
                  AI
                </AvatarFallback>
              </Avatar>
            </Button>
          </DropdownMenuTrigger>
          
          <DropdownMenuContent 
            className="w-56 bg-card/95 backdrop-blur-sm border-border/50 
                     animate-scale-in origin-top-right" 
            align="end"
          >
            <DropdownMenuLabel className="text-primary font-medium">
              Asset Intelligence
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="hover:bg-secondary/50 transition-colors duration-200">
              <User className="mr-2 h-4 w-4" />
              <span>Profile</span>
            </DropdownMenuItem>
            <DropdownMenuItem className="hover:bg-secondary/50 transition-colors duration-200">
              <Settings className="mr-2 h-4 w-4" />
              <span>Settings</span>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="hover:bg-destructive/10 text-destructive 
                                       transition-colors duration-200">
              <LogOut className="mr-2 h-4 w-4" />
              <span>Sign out</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}