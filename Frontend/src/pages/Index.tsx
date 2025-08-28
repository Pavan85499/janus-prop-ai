import { useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { GlobalIntelligence } from "@/components/dashboard/GlobalIntelligence";
import { AgentModules } from "@/components/dashboard/AgentModules";
import { DealTable } from "@/components/dashboard/DealTable";
import { PropertyModal } from "@/components/dashboard/PropertyModal";
import { AskJanusButton } from "@/components/dashboard/AskJanusButton";
import { SidebarProvider } from "@/components/ui/sidebar";

const Index = () => {
  const [selectedProperty, setSelectedProperty] = useState<any>(null);
  const [isPropertyModalOpen, setIsPropertyModalOpen] = useState(false);

  const handlePropertySelect = (property: any) => {
    setSelectedProperty(property);
    setIsPropertyModalOpen(true);
  };

  return (
    <SidebarProvider>
      <div className="min-h-screen w-full bg-background">
        <div className="flex min-h-screen">
          <Sidebar />
          
          <div className="flex-1 flex flex-col">
            <Header />
            
            <main className="flex-1 terminal-grid">
              <div className="space-y-8">
                <GlobalIntelligence />
                <AgentModules />
                <DealTable onPropertySelect={handlePropertySelect} />
              </div>
            </main>
          </div>
        </div>
        
        <PropertyModal
          property={selectedProperty}
          open={isPropertyModalOpen}
          onClose={() => setIsPropertyModalOpen(false)}
        />
        
        <AskJanusButton />
      </div>
    </SidebarProvider>
  );
};

export default Index;