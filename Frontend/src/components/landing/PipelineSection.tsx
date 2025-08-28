import { motion } from "framer-motion";
import { FileText, Home, DollarSign, MapPin, ArrowRight } from "lucide-react";

const dataSources = [
  { name: "County Tax Records", icon: FileText, color: "text-primary" },
  { name: "MLS Listings", icon: Home, color: "text-success" },
  { name: "Rental Databases", icon: DollarSign, color: "text-warning" },
  { name: "Public Liens", icon: MapPin, color: "text-destructive" },
];

export const PipelineSection = () => {
  return (
    <section className="py-32 px-6 bg-background">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          viewport={{ once: true }}
          className="text-center mb-20"
        >
          <h2 className="font-display text-5xl md:text-6xl text-foreground mb-6">
            Real-Time Data
            <br />
            <span className="text-success">
              Pipeline
            </span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Watch as raw data flows through our intelligence engine,
            emerging as actionable investment insights
          </p>
        </motion.div>

        {/* Clean, centered layout - Fixed overlapping issue */}
        <div className="space-y-16">
          {/* Central Processing Hub - Properly contained */}
          <div className="flex justify-center">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.4, delay: 0.1 }}
              viewport={{ once: true }}
              className="institutional-card p-12 w-56 h-56 flex items-center justify-center relative"
            >
              <div className="text-success font-display text-lg font-bold text-center">
                JANUS
                <br />
                <span className="text-sm font-normal text-muted-foreground">AI CORE</span>
              </div>
              
              {/* Contained indicator rings */}
              {[...Array(2)].map((_, i) => (
                <motion.div
                  key={i}
                  className="absolute border border-success/20 pointer-events-none"
                  style={{
                    width: `${240 + i * 24}px`,
                    height: `${240 + i * 24}px`,
                  }}
                  animate={{
                    opacity: [0.1, 0.3, 0.1],
                  }}
                  transition={{
                    duration: 4,
                    repeat: Infinity,
                    delay: i * 1.5,
                  }}
                />
              ))}
            </motion.div>
          </div>

          {/* Data Source Grid - Clean spacing */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {dataSources.map((source, index) => {
              const IconComponent = source.icon;
              
              return (
                <motion.div
                  key={source.name}
                  initial={{ 
                    opacity: 0, 
                    y: 15
                  }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.05 }}
                  viewport={{ once: true }}
                  className="institutional-panel p-6"
                >
                  <div className="flex items-center gap-4 mb-4">
                    <div className="w-10 h-10 bg-card border border-border flex items-center justify-center">
                      <IconComponent className="w-5 h-5 text-success" />
                    </div>
                    <h3 className="text-lg font-medium text-foreground font-display">{source.name}</h3>
                  </div>
                  
                  <div className="ai-status-active inline-flex items-center gap-2 text-sm px-3 py-1">
                    <div className="w-2 h-2 bg-success animate-pulse" />
                    Live Stream
                  </div>
                </motion.div>
              );
            })}
          </div>

          {/* Data Flow Visualization */}
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ duration: 0.4, delay: 0.3 }}
            viewport={{ once: true }}
            className="text-center institutional-panel p-8"
          >
            <div className="flex items-center justify-center gap-8 text-lg flex-wrap">
              <span className="text-muted-foreground font-display">Raw Data</span>
              <ArrowRight className="text-success" />
              <span className="text-success font-medium font-display">AI Processing</span>
              <ArrowRight className="text-success" />
              <span className="text-foreground font-medium font-display">Investment Intelligence</span>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};