import { motion } from "framer-motion";
import { Radar, AlertTriangle, Target, TrendingUp, Building2, Briefcase } from "lucide-react";
import { Button } from "@/components/ui/button";

const mockLienData = [
  {
    property: "183 Rose Ave",
    taxDebt: "$9,000",
    riskScore: "High",
    riskColor: "text-destructive",
    strategy: "Hold lien → wait 12m",
    redemptionOdds: "47.3%"
  },
  {
    property: "520 Bay Rd", 
    taxDebt: "$4,200",
    riskScore: "Medium",
    riskColor: "text-warning",
    strategy: "Buy + flip deed",
    redemptionOdds: "61.0%"
  }
];

const lienAgents = [
  { name: "Ingestion Agent", description: "Pulls liens from counties", status: "active" },
  { name: "Enrichment Agent", description: "Adds visual + zip analytics", status: "active" },
  { name: "Risk Agent", description: "Predicts default & redemption", status: "processing" },
  { name: "Strategy Agent", description: "Builds playbook: hold, flip, wait", status: "active" }
];

const investorTypes = [
  {
    icon: TrendingUp,
    title: "Lien Investor",
    description: "Score, filter, and execute faster with Janus AI."
  },
  {
    icon: Building2,
    title: "Fix-and-Flip Operator", 
    description: "Spot early-stage distress before the market sees it."
  },
  {
    icon: Briefcase,
    title: "Institutional Fund",
    description: "Feed lien data into your existing pipeline via API."
  }
];

export const LienIntelligenceSection = () => {
  return (
    <section className="professional-section bg-background">
      <div className="professional-container">
        {/* Section Title & Intro */}
        <div className="text-center mb-16">
          <motion.h2
            initial={{ opacity: 0, x: -50 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-4xl md:text-5xl font-display text-foreground mb-4"
          >
            Janus Lien Intelligence
          </motion.h2>
          
          <motion.h3
            initial={{ opacity: 0, x: 50 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            viewport={{ once: true }}
            className="text-xl md:text-2xl text-primary font-medium mb-6"
          >
            Turn hidden distress into profitable opportunity.
          </motion.h3>
          
          <motion.p
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            viewport={{ once: true }}
            className="text-lg text-muted-foreground max-w-4xl mx-auto"
          >
            AI-powered lien analytics and distressed property predictions across the U.S. — 
            sourced, scored, and strategy-mapped by Janus agents.
          </motion.p>
        </div>

        {/* Lien Radar Feature Block */}
        <div className="mb-20">
          <motion.h3
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            viewport={{ once: true }}
            className="text-2xl font-display text-foreground mb-12 text-center"
          >
            AI-Powered Lien Analysis Tools
          </motion.h3>
          
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: Radar,
                title: "Lien Risk Radar",
                description: "Track redemption likelihood, tax debt levels, and risk exposure in real time.",
                direction: "left"
              },
              {
                icon: AlertTriangle,
                title: "Pre-Foreclosure Watchlist",
                description: "Automated scanning of eviction filings, code violations, and legal notices.",
                direction: "up"
              },
              {
                icon: Target,
                title: "Redemption Model",
                description: "Predict how likely a lien is to lead to ownership, by state and time window.",
                direction: "right"
              }
            ].map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ 
                  opacity: 0, 
                  x: feature.direction === "left" ? -50 : feature.direction === "right" ? 50 : 0,
                  y: feature.direction === "up" ? 30 : 0
                }}
                whileInView={{ opacity: 1, x: 0, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.2 }}
                viewport={{ once: true }}
                className="data-card text-center"
              >
                <feature.icon className="w-12 h-12 text-primary mx-auto mb-6" />
                <h4 className="text-lg font-medium text-foreground mb-4">{feature.title}</h4>
                <p className="text-muted-foreground">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Scoring Dashboard Preview */}
        <div className="mb-20">
          <motion.h3
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            viewport={{ once: true }}
            className="text-2xl font-display text-foreground mb-8 text-center"
          >
            Live Lien Scoring Dashboard
          </motion.h3>
          
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7 }}
            viewport={{ once: true }}
            className="data-card"
          >
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left py-4 px-4 font-medium text-foreground">Property</th>
                    <th className="text-left py-4 px-4 font-medium text-foreground">Tax Debt</th>
                    <th className="text-left py-4 px-4 font-medium text-foreground">Risk Score</th>
                    <th className="text-left py-4 px-4 font-medium text-foreground">AI Strategy</th>
                    <th className="text-left py-4 px-4 font-medium text-foreground">Redemption Odds</th>
                  </tr>
                </thead>
                <tbody>
                  {mockLienData.map((item, index) => (
                    <motion.tr
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.5, delay: index * 0.1 }}
                      viewport={{ once: true }}
                      className="deal-row"
                    >
                      <td className="py-4 px-4 text-foreground font-medium">{item.property}</td>
                      <td className="py-4 px-4 text-foreground">{item.taxDebt}</td>
                      <td className="py-4 px-4">
                        <span className={`font-medium ${item.riskColor}`}>{item.riskScore}</span>
                      </td>
                      <td className="py-4 px-4 text-muted-foreground italic">{item.strategy}</td>
                      <td className="py-4 px-4 font-medium text-success">{item.redemptionOdds}</td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
            
            <div className="mt-6 text-center">
              <Button variant="outline" className="btn-professional">
                Upload Your Lien List
              </Button>
            </div>
          </motion.div>
        </div>

        {/* Lien Agent Pipeline */}
        <div className="mb-20">
          <motion.h3
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            viewport={{ once: true }}
            className="text-2xl font-display text-foreground mb-12 text-center"
          >
            Lien Analysis Pipeline
          </motion.h3>
          
          <div className="max-w-2xl mx-auto">
            {lienAgents.map((agent, index) => (
              <motion.div
                key={agent.name}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.15 }}
                viewport={{ once: true }}
                className="flex items-center mb-8 last:mb-0"
              >
                <div className="relative mr-6">
                  <div className={`w-4 h-4 rounded-full ${
                    agent.status === 'active' ? 'bg-success' : 
                    agent.status === 'processing' ? 'bg-highlight' : 'bg-muted'
                  }`}>
                    {agent.status === 'processing' && (
                      <div className="absolute inset-0 rounded-full bg-highlight animate-ping"></div>
                    )}
                  </div>
                  {index < lienAgents.length - 1 && (
                    <div className="absolute top-4 left-1/2 transform -translate-x-1/2 w-0.5 h-12 bg-border"></div>
                  )}
                </div>
                
                <div className="flex-1 data-card">
                  <h4 className="font-medium text-foreground mb-2">{agent.name}</h4>
                  <p className="text-muted-foreground">{agent.description}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Investor Use Cases */}
        <div className="mb-20">
          <motion.h3
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            viewport={{ once: true }}
            className="text-2xl font-display text-foreground mb-12 text-center"
          >
            Built for Every Investor Type
          </motion.h3>
          
          <div className="grid md:grid-cols-3 gap-8">
            {investorTypes.map((type, index) => (
              <motion.div
                key={type.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.2 }}
                viewport={{ once: true }}
                className="data-card text-center hover:shadow-professional transition-all duration-300"
              >
                <type.icon className="w-12 h-12 text-primary mx-auto mb-6" />
                <h4 className="text-lg font-medium text-foreground mb-4">{type.title}</h4>
                <p className="text-muted-foreground">{type.description}</p>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Final CTA */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="bg-secondary rounded-lg p-12 text-center"
        >
          <h3 className="text-2xl font-display text-foreground mb-6">
            Upload your liens. Let Janus do the thinking.
          </h3>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button className="btn-professional">
              Request Demo
            </Button>
            <Button variant="outline" className="btn-professional border-primary">
              Join the Beta Waitlist
            </Button>
          </div>
        </motion.div>
      </div>
    </section>
  );
};