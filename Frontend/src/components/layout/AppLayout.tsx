import { ReactNode } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { SidebarProvider } from "@/components/ui/sidebar";

interface AppLayoutProps {
  children: ReactNode;
  showSidebar?: boolean;
  className?: string;
}

export function AppLayout({ 
  children, 
  showSidebar = true, 
  className = "" 
}: AppLayoutProps) {
  if (!showSidebar) {
    return (
      <div className={`min-h-screen w-full bg-background ${className}`}>
        {children}
      </div>
    );
  }

  return (
    <SidebarProvider>
      <div className="min-h-screen w-full bg-background">
        <div className="flex min-h-screen">
          <Sidebar />
          
          <div className="flex-1 flex flex-col min-w-0">
            <Header />
            
            <main className={`flex-1 responsive-container ${className}`}>
              {children}
            </main>
          </div>
        </div>
      </div>
    </SidebarProvider>
  );
}
