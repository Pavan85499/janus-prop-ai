import { motion } from "framer-motion";
import { 
  Target,
  Network,
  BarChart3,
  Zap
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

const processSteps = [
  {
    step: "1",
    title: "Ingest",
    description: "Millions of liens, filings, and property records, pulled daily"
  },
  {
    step: "2",
    title: "Analyze", 
    description: "Agents interpret each signal independently"
  },
  {
    step: "3",
    title: "Score",
    description: "Investment potential is ranked by ROI, risk, timing"
  },
  {
    step: "4",
    title: "Forecast",
    description: "Neighborhood demand, redemption outcomes, rent"
  },
  {
    step: "5", 
    title: "Deliver",
    description: "Reports, alerts, and actionable insights"
  },
  {
    step: "6",
    title: "Feedback",
    description: "System learns with every action and user decision"
  }
];

const advantages = [
  {
    icon: Target,
    title: "We pull data no one else does — deep legal and municipal filings"
  },
  {
    icon: Network, 
    title: "We use a true AI agent architecture — modular and adaptive"
  },
  {
    icon: BarChart3,
    title: "We don't give dashboards. We give decisions."
  },
  {
    icon: Zap,
    title: "Every week, the system gets smarter."
  }
];

export const JanusIntelligenceEngineSection = () => {
  return (
    <section className="professional-section bg-background text-foreground">
      <div className="professional-container">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-20"
        >
          <h2 className="text-5xl md:text-6xl font-display font-bold mb-6 text-foreground">
            Janus AI: The Real Estate Intelligence Engine
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            A system of autonomous agents built to think, reason, and execute like elite real estate investors.
          </p>
        </motion.div>

        {/* Process Flow */}
        <div className="mb-32">
          <motion.h3
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="text-3xl font-display font-bold mb-12 text-center text-foreground"
          >
            How Janus Works
          </motion.h3>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {processSteps.map((step, index) => (
              <motion.div
                key={step.step}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: index * 0.1 }}
              >
                <Card className="institutional-card h-full">
                  <CardContent className="p-6">
                    <div className="flex items-center gap-4 mb-4">
                      <div className="w-12 h-12 rounded-full bg-accent flex items-center justify-center text-white font-bold text-lg">
                        {step.step}
                      </div>
                      <h4 className="font-display font-bold text-xl text-foreground">
                        {step.title}
                      </h4>
                    </div>
                    <p className="text-muted-foreground leading-relaxed">
                      {step.description}
                    </p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Why We Win */}
        <div>
          <motion.h3
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="text-3xl font-display font-bold mb-12 text-center text-foreground"
          >
            Why We Win
          </motion.h3>

          <div className="space-y-6">
            {advantages.map((advantage, index) => {
              const IconComponent = advantage.icon;
              return (
                <motion.div
                  key={advantage.title}
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.4, delay: index * 0.1 }}
                >
                  <Card className="institutional-card">
                    <CardContent className="p-6">
                      <div className="flex items-center gap-6">
                        <div className="p-3 rounded-lg bg-accent/10 text-accent shrink-0">
                          <IconComponent className="w-6 h-6" />
                        </div>
                        <p className="text-lg text-muted-foreground leading-relaxed">
                          {advantage.title}
                        </p>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
};