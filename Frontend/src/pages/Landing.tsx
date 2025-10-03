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
      
      {/* Hero Section with Animatic Entrance */}
      <div id="hero" className="responsive-fade-in">
        <HeroSection />
      </div>
      
      {/* Lien Intelligence with Staggered Animation */}
      <div id="lien-intelligence" className="responsive-slide-in-left">
        <LienIntelligenceSection />
      </div>
      
      {/* Intelligence Engine with Scale Animation */}
      <div id="intelligence-engine" className="responsive-scale-in">
        <JanusIntelligenceEngineSection />
      </div>
      
      {/* Agents with Staggered Cards */}
      <div id="agents" className="responsive-fade-in">
        <JanusAgentsSection />
      </div>
      
      {/* Dashboard with Grid Animation */}
      <div id="dashboard" className="responsive-slide-in-right">
        <MainDashboard />
      </div>
      
      {/* Market Intelligence with Fade Up */}
      <div id="market-intelligence" className="responsive-fade-in">
        <MarketIntelligence />
      </div>
      
      {/* Pipeline with Slide Animation */}
      <div id="pipeline" className="responsive-slide-in-left">
        <PipelineSection />
      </div>
      
      {/* Architecture with Scale Animation */}
      <div id="architecture" className="responsive-scale-in">
        <DealIntelligenceSection />
      </div>
      
      {/* Leads with Fade Animation */}
      <div id="leads" className="responsive-fade-in">
        <LeadManagement />
      </div>
      
      {/* Demo with Bounce Animation */}
      <div id="demo" className="responsive-fade-in">
        <ClosingSection />
      </div>
    </div>
  );
};

export default Landing;