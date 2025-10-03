import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import { usePageTransition } from "@/hooks/useAnimatic";
import Landing from "./pages/Landing";
import Index from "./pages/Index";
import BackendTest from "./pages/BackendTest";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import ScheduleDemo from "./pages/ScheduleDemo";
import Agents from "./pages/Agents";
import Properties from "./pages/Properties";
import Portfolios from "./pages/Portfolios";
import DealRoom from "./pages/DealRoom";
import Analytics from "./pages/Analytics";
import Automation from "./pages/Automation";
import Settings from "./pages/Settings";
import PropertyScanner from "./pages/PropertyScanner";
import DocumentManagement from "./pages/DocumentManagement";
import Underwriting from "./pages/Underwriting";
import LegalCompliance from "./pages/LegalCompliance";
import AIInvestmentCommittee from "./pages/AIInvestmentCommittee";
import ExecutionClosing from "./pages/ExecutionClosing";
import PostAcquisition from "./pages/PostAcquisition";
import SubscriptionManagement from "./pages/SubscriptionManagement";
import NotFound from "./pages/NotFound";
import { AskJanusProvider } from "./contexts/AskJanusContext";
import AskJanusOverlay from "./components/dashboard/AskJanusOverlay";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <AuthProvider>
        <AskJanusProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/dashboard" element={<Index />} />
            <Route path="/schedule-demo" element={<ScheduleDemo />} />
            <Route path="/agents" element={<Agents />} />
            <Route path="/properties" element={<Properties />} />
            <Route path="/portfolios" element={<Portfolios />} />
            <Route path="/deals" element={<DealRoom />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/automation" element={<Automation />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/property-scanner" element={<PropertyScanner />} />
            <Route path="/documents" element={<DocumentManagement />} />
            <Route path="/underwriting" element={<Underwriting />} />
            <Route path="/legal-compliance" element={<LegalCompliance />} />
            <Route path="/investment-committee" element={<AIInvestmentCommittee />} />
            <Route path="/execution-closing" element={<ExecutionClosing />} />
            <Route path="/post-acquisition" element={<PostAcquisition />} />
            <Route path="/subscription" element={<SubscriptionManagement />} />
            <Route path="/backend-test" element={<BackendTest />} />
            {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
            <Route path="*" element={<NotFound />} />
          </Routes>
          <AskJanusOverlay />
        </BrowserRouter>
        </AskJanusProvider>
      </AuthProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
