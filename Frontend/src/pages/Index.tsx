import { useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { GlobalIntelligence } from "@/components/dashboard/GlobalIntelligence";
import { AgentModules } from "@/components/dashboard/AgentModules";
import { DealTable } from "@/components/dashboard/DealTable";
import { PropertyModal } from "@/components/dashboard/PropertyModal";
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
              <div className="responsive-padding animatic-container">
                <Tabs defaultValue="overview" className="w-full">
                  <TabsList className="grid w-full grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 
                                    bg-card/50 border border-border/50 rounded-lg p-1
                                    responsive-fade-in responsive-scroll-horizontal">
                    <TabsTrigger 
                      value="overview" 
                      className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground
                               transition-all duration-300 hover:scale-105 focus-ring touch-target"
                    >
                      <span className="mobile-only">Overview</span>
                      <span className="tablet-up">Overview</span>
                    </TabsTrigger>
                    <TabsTrigger 
                      value="ai-insights"
                      className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground
                               transition-all duration-300 hover:scale-105 focus-ring touch-target"
                    >
                      <span className="mobile-only">AI</span>
                      <span className="tablet-up">AI Insights</span>
                    </TabsTrigger>
                    <TabsTrigger 
                      value="data-integration"
                      className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground
                               transition-all duration-300 hover:scale-105 focus-ring touch-target"
                    >
                      <span className="mobile-only">Data</span>
                      <span className="tablet-up">Data Integration</span>
                    </TabsTrigger>
                    <TabsTrigger 
                      value="learning"
                      className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground
                               transition-all duration-300 hover:scale-105 focus-ring touch-target"
                    >
                      <span className="mobile-only">Learn</span>
                      <span className="tablet-up">Learning</span>
                    </TabsTrigger>
                    <TabsTrigger 
                      value="agents"
                      className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground
                               transition-all duration-300 hover:scale-105 focus-ring touch-target"
                    >
                      <span className="mobile-only">Agents</span>
                      <span className="tablet-up">Agents</span>
                    </TabsTrigger>
                  </TabsList>
                  
                  <TabsContent value="overview" className="space-y-6 sm:space-y-8 animate-fade-in-up">
                    <div className="card-stagger-1">
                      <GlobalIntelligence />
                    </div>
                    <div className="card-stagger-2">
                      <AgentModules />
                    </div>
                  </TabsContent>
                  
                  <TabsContent value="ai-insights" className="space-y-4 sm:space-y-6 animate-fade-in-up">
                    <div className="card-stagger-1">
                      <AIInsightsPanel 
                        analysis={mockPropertyAnalysis}
                        onActionClick={handleActionClick}
                      />
                    </div>
                  </TabsContent>
                  
                  <TabsContent value="data-integration" className="space-y-4 sm:space-y-6 animate-fade-in-up">
                    <div className="card-stagger-1">
                      <DataIntegrationDashboard 
                        onSyncSource={handleSyncSource}
                        onAddSource={handleAddSource}
                      />
                    </div>
                  </TabsContent>
                  
                  <TabsContent value="learning" className="space-y-4 sm:space-y-6 animate-fade-in-up">
                    <div className="card-stagger-1">
                      <LearningMetricsDashboard 
                        onExportData={handleExportData}
                        onGenerateReport={handleGenerateReport}
                      />
                    </div>
                  </TabsContent>
                  
                  <TabsContent value="agents" className="space-y-6 sm:space-y-8 animate-fade-in-up">
                    <div className="space-y-6 sm:space-y-8">
                      <div className="card-stagger-1">
                        <GlobalIntelligence />
                      </div>
                      <div className="card-stagger-2">
                        <AgentModules />
                      </div>
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
      </div>
    </SidebarProvider>
  );
};

export default Index;