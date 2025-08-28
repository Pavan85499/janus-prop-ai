import { useState } from "react";
import { Button } from "@/components/ui/button";
import { MessageSquare, X, Send } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";

export function AskJanusButton() {
  const [isOpen, setIsOpen] = useState(false);
  const [message, setMessage] = useState("");

  const suggestions = [
    "Find properties with 10%+ cap rates",
    "Show me BRRRR opportunities in Austin",
    "What's the market trend for tax liens?",
    "Analyze my portfolio diversification"
  ];

  return (
    <>
      {/* Floating Button */}
      <div className="fixed bottom-6 right-6 z-50">
        {!isOpen && (
          <Button 
            onClick={() => setIsOpen(true)}
            className="h-14 w-14 rounded-full bg-gradient-primary glow-primary shadow-2xl hover:scale-105 transition-all duration-200"
          >
            <MessageSquare className="w-6 h-6" />
          </Button>
        )}
      </div>

      {/* Chat Interface */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 z-50 w-96">
          <Card className="data-card shadow-2xl">
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                  <MessageSquare className="w-4 h-4 text-primary-foreground" />
                </div>
                <div>
                  <CardTitle className="text-lg font-normal">Ask Janus</CardTitle>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-success rounded-full animate-pulse"></div>
                    <span className="text-xs text-muted-foreground">AI Assistant Online</span>
                  </div>
                </div>
              </div>
              
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => setIsOpen(false)}
              >
                <X className="w-4 h-4" />
              </Button>
            </CardHeader>
            
            <CardContent className="space-y-4">
              {/* Welcome Message */}
              <div className="p-3 bg-primary/10 rounded-lg border border-primary/20">
                <p className="text-sm">
                  <span className="font-medium text-primary">Janus AI:</span> How can I help you analyze the real estate market today?
                </p>
              </div>

              {/* Quick Suggestions */}
              <div className="space-y-2">
                <p className="text-xs text-muted-foreground font-medium">Quick Actions:</p>
                <div className="grid grid-cols-1 gap-2">
                  {suggestions.map((suggestion, index) => (
                    <Badge 
                      key={index}
                      variant="outline" 
                      className="justify-start text-left p-2 h-auto cursor-pointer hover:bg-primary/10 hover:border-primary/30 transition-colors"
                      onClick={() => setMessage(suggestion)}
                    >
                      {suggestion}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Message Input */}
              <div className="flex gap-2">
                <Input 
                  placeholder="Ask about properties, market trends..."
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  className="bg-secondary/20 border-border/50"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      // Handle message send
                      setMessage("");
                    }
                  }}
                />
                <Button 
                  size="sm" 
                  className="bg-gradient-primary glow-primary shrink-0"
                  disabled={!message.trim()}
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
              
              <p className="text-xs text-muted-foreground">
                Powered by GPT-4 with real-time market data
              </p>
            </CardContent>
          </Card>
        </div>
      )}
    </>
  );
}