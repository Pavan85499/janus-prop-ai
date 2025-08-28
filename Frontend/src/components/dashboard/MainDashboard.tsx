import { useState } from "react";
import { SmartFilters } from "./SmartFilters";
import { MapListView } from "./MapListView";
import { PropertyPreview } from "./PropertyPreview";
import { PropertyDetailView } from "./PropertyDetailView";
import { AgentActivityConsole } from "./AgentActivityConsole";
import { AIAgentChat } from "./AIAgentChat";

export function MainDashboard() {
  const [selectedProperty, setSelectedProperty] = useState<any>(null);
  const [detailProperty, setDetailProperty] = useState<any>(null);
  const [isDetailViewOpen, setIsDetailViewOpen] = useState(false);

  const handlePropertySelect = (property: any) => {
    setSelectedProperty(property);
  };

  const handlePropertyDetail = (property: any) => {
    setDetailProperty(property);
    setIsDetailViewOpen(true);
  };

  return (
    <section className="bg-background">
      <div className="h-screen flex">
        {/* Left Panel - Smart Filters */}
        <SmartFilters />
        
        {/* Center Panel - Map & List Toggle */}
        <MapListView 
          onPropertySelect={handlePropertySelect}
          onPropertyDetail={handlePropertyDetail}
        />
        
        {/* Right Panel - Property Preview & AI Insight */}
        <PropertyPreview property={selectedProperty} />
        
        {/* Floating Agent Activity Console */}
        <AgentActivityConsole />

        {/* AI Agent Chat Interface */}
        <AIAgentChat />

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