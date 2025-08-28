import { useLocation } from "react-router-dom";
import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Home, ArrowLeft } from "lucide-react";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error(
      "404 Error: User attempted to access non-existent route:",
      location.pathname
    );
  }, [location.pathname]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center space-y-6 max-w-md">
        <div className="space-y-2">
          <h1 className="font-display text-6xl font-normal text-primary">404</h1>
          <h2 className="font-display text-2xl font-normal">Page Not Found</h2>
          <p className="text-muted-foreground">
            The page you're looking for doesn't exist in the Janus AI platform.
          </p>
        </div>
        
        <div className="flex gap-4 justify-center">
          <Button 
            variant="outline" 
            onClick={() => window.history.back()}
            className="border-border/50 hover:bg-secondary/50"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Go Back
          </Button>
          
          <Button 
            onClick={() => window.location.href = "/"}
            className="bg-gradient-primary glow-primary"
          >
            <Home className="w-4 h-4 mr-2" />
            Return to Dashboard
          </Button>
        </div>
      </div>
    </div>
  );
};

export default NotFound;
