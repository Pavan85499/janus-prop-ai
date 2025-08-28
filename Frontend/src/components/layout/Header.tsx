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
import { Plus, User, Settings, LogOut, MessageSquare } from "lucide-react";

export function Header() {
  return (
    <header className="h-16 border-b border-border/50 bg-card/30 backdrop-blur-lg flex items-center justify-between px-6">
      <div className="flex items-center gap-4">
        <SidebarTrigger className="text-muted-foreground hover:text-foreground" />
        
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-success rounded-full animate-pulse"></div>
          <span className="text-sm text-muted-foreground">Real-time Intelligence Active</span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <Button 
          variant="default" 
          size="sm" 
          className="bg-gradient-primary hover:bg-primary/90 glow-primary"
        >
          <Plus className="w-4 h-4 mr-2" />
          Add New Property
        </Button>
        
        <Button 
          variant="outline" 
          size="sm"
          className="border-primary/30 text-primary hover:bg-primary/10"
        >
          <MessageSquare className="w-4 h-4 mr-2" />
          Ask Janus
        </Button>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="relative h-8 w-8 rounded-full">
              <Avatar className="h-8 w-8">
                <AvatarImage src="/placeholder.svg" alt="User" />
                <AvatarFallback className="bg-primary text-primary-foreground">
                  AI
                </AvatarFallback>
              </Avatar>
            </Button>
          </DropdownMenuTrigger>
          
          <DropdownMenuContent className="w-56 bg-card/95 backdrop-blur-sm border-border/50" align="end">
            <DropdownMenuLabel>Asset Intelligence</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem>
              <User className="mr-2 h-4 w-4" />
              <span>Profile</span>
            </DropdownMenuItem>
            <DropdownMenuItem>
              <Settings className="mr-2 h-4 w-4" />
              <span>Settings</span>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem>
              <LogOut className="mr-2 h-4 w-4" />
              <span>Sign out</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}