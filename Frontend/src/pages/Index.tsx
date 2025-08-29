import { useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { GlobalIntelligence } from "@/components/dashboard/GlobalIntelligence";
import { AgentModules } from "@/components/dashboard/AgentModules";
import { DealTable } from "@/components/dashboard/DealTable";
import { PropertyModal } from "@/components/dashboard/PropertyModal";
import { AskJanusButton } from "@/components/dashboard/AskJanusButton";
import { SidebarProvider } from "@/components/ui/sidebar";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import AIInsightsPanel from "@/components/dashboard/AIInsightsPanel";
import DataIntegrationDashboard from "@/components/dashboard/DataIntegrationDashboard";
import LearningMetricsDashboard from "@/components/dashboard/LearningMetricsDashboard";

const Index = () => {
  const [selectedProperty, setSelectedProperty] = useState<any>(null);
  const [isPropertyModalOpen, setIsPropertyModalOpen] = useState(false);

  const handlePropertySelect = (property: any) => {
    setSelectedProperty(property);
    setIsPropertyModalOpen(true);
  };

  // Mock data for AI Insights
  const mockPropertyAnalysis = {
    property_id: "prop_123",
    insights: [
      {
        insight_id: "insight_1",
        insight_type: "market_opportunity",
        confidence_score: 0.85,
        explanation: "Property values in this area are increasing by 5-8% annually, indicating strong market momentum and potential for appreciation.",
        actionable_steps: [
          "Consider purchasing before prices increase further",
          "Research comparable sales in the area",
          "Consult with local real estate agents about market timing"
        ],
        data_sources: ["market_analysis", "price_trends", "local_economic_data"]
      },
      {
        insight_id: "insight_2",
        insight_type: "risk_assessment",
        confidence_score: 0.80,
        explanation: "Risk assessment based on: Low risk profile with stable market conditions. Overall risk level: Low.",
        actionable_steps: [
          "Conduct thorough property inspection",
          "Review local crime statistics and safety reports",
          "Consult with insurance providers about coverage options"
        ],
        data_sources: ["property_inspection", "crime_statistics", "market_analysis"]
      },
      {
        insight_id: "insight_3",
        insight_type: "investment_potential",
        confidence_score: 0.75,
        explanation: "Based on current market data, this property shows a potential annual ROI of 7.2%. This compares favorably to the local market average of 6-8%.",
        actionable_steps: [
          "Calculate detailed cash flow projections",
          "Compare with other investment properties in the area",
          "Consult with financial advisor about financing options"
        ],
        data_sources: ["financial_analysis", "market_comparisons", "rental_data"]
      }
    ],
    overall_score: 0.80,
    summary: "This property shows strong potential with multiple positive indicators.",
    next_steps: [
      "Schedule property inspection",
      "Get pre-approval for financing",
      "Research comparable properties in the area"
    ]
  };

  const handleActionClick = (action: string, insightId: string) => {
    console.log(`Action clicked: ${action} for insight: ${insightId}`);
    // In production, this would trigger specific workflows
  };

  const handleSyncSource = (sourceId: string) => {
    console.log(`Syncing data source: ${sourceId}`);
    // In production, this would call the backend API
  };

  const handleAddSource = (sourceConfig: any) => {
    console.log(`Adding new data source:`, sourceConfig);
    // In production, this would call the backend API
  };

  const handleExportData = () => {
    console.log("Exporting learning data");
    // In production, this would generate and download a report
  };

  const handleGenerateReport = () => {
    console.log("Generating learning report");
    // In production, this would create a comprehensive report
  };

  return (
    <SidebarProvider>
      <div className="min-h-screen w-full bg-background">
        <div className="flex min-h-screen">
          <Sidebar />
          
          <div className="flex-1 flex flex-col">
            <Header />
            
            <main className="flex-1 terminal-grid">
              <div className="p-6">
                <Tabs defaultValue="overview" className="w-full">
                  <TabsList className="grid w-full grid-cols-5">
                    <TabsTrigger value="overview">Overview</TabsTrigger>
                    <TabsTrigger value="ai-insights">AI Insights</TabsTrigger>
                    <TabsTrigger value="data-integration">Data Integration</TabsTrigger>
                    <TabsTrigger value="learning">Learning Metrics</TabsTrigger>
                    <TabsTrigger value="agents">Agents</TabsTrigger>
                  </TabsList>
                  
                  <TabsContent value="overview" className="space-y-8">
                    <GlobalIntelligence />
                    <AgentModules />
                    <DealTable onPropertySelect={handlePropertySelect} />
                  </TabsContent>
                  
                  <TabsContent value="ai-insights" className="space-y-6">
                    <AIInsightsPanel 
                      analysis={mockPropertyAnalysis}
                      onActionClick={handleActionClick}
                    />
                  </TabsContent>
                  
                  <TabsContent value="data-integration" className="space-y-6">
                    <DataIntegrationDashboard 
                      onSyncSource={handleSyncSource}
                      onAddSource={handleAddSource}
                    />
                  </TabsContent>
                  
                  <TabsContent value="learning" className="space-y-6">
                    <LearningMetricsDashboard 
                      onExportData={handleExportData}
                      onGenerateReport={handleGenerateReport}
                    />
                  </TabsContent>
                  
                  <TabsContent value="agents" className="space-y-6">
                    <div className="space-y-8">
                      <GlobalIntelligence />
                      <AgentModules />
                    </div>
                  </TabsContent>
                </Tabs>
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