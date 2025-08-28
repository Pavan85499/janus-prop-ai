import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { TrendingUp, Eye, Archive } from "lucide-react";

const mockDeals = [
  {
    address: "1247 Oak Street, Austin TX",
    lienScore: 94,
    capRate: "8.2%",
    strategy: "Buy-to-Hold",
    aiSummary: "Prime location, undervalued, strong rental demand",
    riskLevel: "low"
  },
  {
    address: "892 Pine Avenue, Dallas TX",
    lienScore: 87,
    capRate: "7.8%",
    strategy: "Cap Rate Arbitrage",
    aiSummary: "Distressed seller, quick flip opportunity",
    riskLevel: "medium"
  },
  {
    address: "456 Elm Drive, Houston TX",
    lienScore: 76,
    capRate: "6.9%",
    strategy: "Value-Add",
    aiSummary: "Renovation needed, high upside potential",
    riskLevel: "high"
  }
];

const getRiskColor = (risk: string) => {
  switch (risk) {
    case "low": return "bg-[hsl(var(--success))]/10 text-[hsl(var(--success))] border border-[hsl(var(--success))]/20";
    case "medium": return "bg-[hsl(var(--warning))]/10 text-[hsl(var(--warning))] border border-[hsl(var(--warning))]/20";
    case "high": return "bg-[hsl(var(--destructive))]/10 text-[hsl(var(--destructive))] border border-[hsl(var(--destructive))]/20";
    default: return "bg-[hsl(var(--success))]/10 text-[hsl(var(--success))] border border-[hsl(var(--success))]/20";
  }
};

export const DealIntelligenceSection = () => {
  return (
    <section className="py-32 px-6 bg-background">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          viewport={{ once: true }}
          className="text-center mb-20"
        >
          <h2 className="font-display text-5xl md:text-6xl text-foreground mb-6">
            Live Deal
            <br />
            <span className="text-[hsl(var(--success))]">
              Intelligence
            </span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Real-time property analysis with AI-generated investment strategies
            and risk assessment
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          viewport={{ once: true }}
          className="institutional-panel p-8 mb-8"
        >
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-[hsl(var(--border))]">
                  <th className="text-left py-4 px-4 text-foreground font-medium font-display">Property</th>
                  <th className="text-right py-4 px-4 text-foreground font-medium font-display">Lien Score</th>
                  <th className="text-right py-4 px-4 text-foreground font-medium font-display">Cap Rate</th>
                  <th className="text-left py-4 px-4 text-foreground font-medium font-display">Strategy</th>
                  <th className="text-left py-4 px-4 text-foreground font-medium font-display">AI Summary</th>
                  <th className="text-right py-4 px-4 text-foreground font-medium font-display">Actions</th>
                </tr>
              </thead>
              <tbody>
                {mockDeals.map((deal, index) => (
                  <motion.tr
                    key={deal.address}
                    initial={{ opacity: 0, x: -15 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3, delay: 0.3 + index * 0.1 }}
                    viewport={{ once: true }}
                    className="border-b border-[hsl(var(--border))]/30 hover:bg-secondary/30 transition-colors duration-200"
                  >
                    <td className="py-4 px-4">
                      <div className="text-foreground font-medium">{deal.address}</div>
                    </td>
                    <td className="py-4 px-4 text-right">
                      <span className={`inline-flex items-center px-2 py-1 text-xs font-medium ${getRiskColor(deal.riskLevel)}`}>
                        {deal.lienScore}
                      </span>
                    </td>
                    <td className="py-4 px-4 text-right text-[hsl(var(--success))] font-mono">
                      {deal.capRate}
                    </td>
                    <td className="py-4 px-4">
                      <span className="text-muted-foreground text-sm">{deal.strategy}</span>
                    </td>
                    <td className="py-4 px-4">
                      <span className="text-muted-foreground text-sm">{deal.aiSummary}</span>
                    </td>
                    <td className="py-4 px-4 text-right">
                      <div className="flex gap-2 justify-end">
                        <button className="text-[hsl(var(--success))] hover:text-primary text-sm font-medium transition-colors">
                          View
                        </button>
                        <button className="text-muted-foreground hover:text-foreground text-sm font-medium transition-colors">
                          Archive
                        </button>
                      </div>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Loading indicator */}
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.8 }}
            viewport={{ once: true }}
            className="flex items-center justify-center gap-3 mt-8 pt-6 border-t border-[hsl(var(--border))]"
          >
            <div className="flex gap-1">
              {[...Array(3)].map((_, i) => (
                <motion.div
                  key={i}
                  className="w-2 h-2 bg-[hsl(var(--success))]"
                  animate={{
                    opacity: [0.3, 1, 0.3],
                  }}
                  transition={{
                    duration: 1.5,
                    repeat: Infinity,
                    delay: i * 0.2,
                  }}
                />
              ))}
            </div>
            <span className="text-muted-foreground text-sm">
              AI analyzing 847 more properties...
            </span>
          </motion.div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 15 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
          viewport={{ once: true }}
          className="text-center"
        >
          <Button size="lg" className="btn-professional text-lg px-8 py-6">
            Run Your Own Portfolio Analysis
          </Button>
        </motion.div>
      </div>
    </section>
  );
};