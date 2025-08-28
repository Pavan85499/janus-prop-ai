import { HeroSection } from "@/components/landing/HeroSection";
import { LienIntelligenceSection } from "@/components/landing/LienIntelligenceSection";
import { JanusIntelligenceEngineSection } from "@/components/landing/JanusIntelligenceEngineSection";
import { JanusAgentsSection } from "@/components/landing/JanusAgentsSection";
import { MainDashboard } from "@/components/dashboard/MainDashboard";
import { PipelineSection } from "@/components/landing/PipelineSection";
import { DealIntelligenceSection } from "@/components/landing/DealIntelligenceSection";
import { LeadManagement } from "@/components/dashboard/LeadManagement";
import { MarketIntelligence } from "@/components/dashboard/MarketIntelligence";
import { ClosingSection } from "@/components/landing/ClosingSection";
import { ScrollNavigation } from "@/components/landing/ScrollNavigation";

const Landing = () => {
  return (
    <div className="min-h-screen bg-background text-foreground overflow-x-hidden">
      <ScrollNavigation />
      <div id="hero">
        <HeroSection />
      </div>
      <div id="lien-intelligence">
        <LienIntelligenceSection />
      </div>
      <div id="intelligence-engine">
        <JanusIntelligenceEngineSection />
      </div>
      <div id="agents">
        <JanusAgentsSection />
      </div>
      <div id="dashboard">
        <MainDashboard />
      </div>
      <div id="market-intelligence">
        <MarketIntelligence />
      </div>
      <div id="pipeline">
        <PipelineSection />
      </div>
      <div id="architecture">
        <DealIntelligenceSection />
      </div>
      <div id="leads">
        <LeadManagement />
      </div>
      <div id="demo">
        <ClosingSection />
      </div>
    </div>
  );
};

export default Landing;