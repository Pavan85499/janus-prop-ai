import { useState } from "react";
import { MapListView } from "./MapListView";
import { PropertyPreview } from "./PropertyPreview";
import { PropertyDetailView } from "./PropertyDetailView";
import { AgentActivityConsole } from "./AgentActivityConsole";
import { AIAgentChat } from "./AIAgentChat";
import { BackendStatusIndicator } from "../ui/BackendStatusIndicator";

interface Property {
  id: string;
  address: string;
  price: number;
  estimatedValue: number;
  equity: number;
  type: string;
  beds: number;
  baths: number;
  sqft: number;
  janusScore: number;
  distressLevel: string;
  image: string;
  daysOnMarket?: number;
}

export function MainDashboard() {
  const [selectedProperty, setSelectedProperty] = useState<Property | null>(null);
  const [detailProperty, setDetailProperty] = useState<Property | null>(null);
  const [isDetailViewOpen, setIsDetailViewOpen] = useState(false);

  const handlePropertySelect = (property: Property) => {
    setSelectedProperty(property);
  };

  const handlePropertyDetail = (property: Property) => {
    setDetailProperty(property);
    setIsDetailViewOpen(true);
  };

  return (
    <section className="bg-background">
      <div className="h-screen flex flex-col lg:flex-row">
        {/* Center Panel - Map & List Toggle */}
        <div className="flex-1 flex flex-col min-h-0">
          <MapListView 
            onPropertySelect={handlePropertySelect}
            onPropertyDetail={handlePropertyDetail}
          />
        </div>
        
        {/* Right Panel - Property Preview & AI Insight */}
        <div className="w-full lg:w-96 border-t lg:border-t-0 lg:border-l border-border bg-card overflow-y-auto">
          <PropertyPreview property={selectedProperty} />
        </div>
        
        {/* Floating Agent Activity Console */}
        <AgentActivityConsole />

        {/* AI Agent Chat Interface */}
        <AIAgentChat />

        {/* Backend Status Indicator */}
        <div className="fixed top-4 right-4 z-50">
          <BackendStatusIndicator showDetails={false} />
        </div>

        {/* Property Detail Modal */}
        <PropertyDetailView
          property={detailProperty}
          open={isDetailViewOpen}
          onClose={() => setIsDetailViewOpen(false)}
        />
      </div>
    </section>
  );
}