import { motion } from "framer-motion";

const agents = [
  {
    name: "Eden",
    role: "Executive Strategist",
    description: "Makes final investment decisions using all agent signals and ranks deals by return and fit."
  },
  {
    name: "Orion", 
    role: "Market Intelligence Scanner",
    description: "Monitors and collects tax liens, auctions, violations, and court activity in real time."
  },
  {
    name: "Atelius",
    role: "Legal Intelligence Agent",
    description: "Parses court filings, redemption rules, legal risks, and title chains."
  },
  {
    name: "Osiris",
    role: "Financial Modeler", 
    description: "Projects returns, redemption windows, and yield forecasts on every deal."
  },
  {
    name: "Celestia",
    role: "Report Generator",
    description: "Creates investor-ready memos, overviews, and PDFs for every opportunity."
  },
  {
    name: "Valyria",
    role: "Market Forecaster",
    description: "Analyzes migration, rental demand, and zip-code-level shifts to predict price movement."
  },
  {
    name: "Spring",
    role: "Quality Control & Audit Agent",
    description: "Reviews all outputs for accuracy, completeness, and logic."
  },
  {
    name: "Elysia",
    role: "Data Integrator",
    description: "Cleans, enriches, and joins external data (e.g., Redfin, Zillow, gov filings)."
  },
  {
    name: "Aurora",
    role: "Workflow Orchestrator",
    description: "Coordinates all agents, routes tasks, and ensures real-time flow of intelligence."
  }
];

export const JanusAgentsSection = () => {
  return (
    <section className="professional-section bg-background text-foreground">
      <div className="professional-container">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-display font-normal mb-6 text-foreground">
            Janus AI Agents
          </h2>
          <p className="text-lg text-muted-foreground max-w-3xl mx-auto">
            The Intelligence Engine
          </p>
        </motion.div>

        {/* Agent Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {agents.map((agent, index) => {
            const isLeft = index % 2 === 0;
            
            return (
              <motion.div
                key={agent.name}
                initial={{ opacity: 0, x: isLeft ? -30 : 30 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ 
                  duration: 0.5, 
                  delay: index * 0.1,
                  ease: "easeOut"
                }}
                className="h-full"
              >
                <div className="institutional-card h-full p-8">
                  <h3 className="text-2xl font-display font-normal text-foreground mb-2">
                    {agent.name}
                  </h3>
                  <h4 className="text-sm font-medium text-primary mb-4 uppercase tracking-wider">
                    {agent.role}
                  </h4>
                  <p className="text-muted-foreground leading-relaxed">
                    {agent.description}
                  </p>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
};