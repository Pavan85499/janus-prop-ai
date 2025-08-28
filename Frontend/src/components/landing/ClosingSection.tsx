import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Brain } from "lucide-react";

export const ClosingSection = () => {
  return (
    <section className="professional-section bg-secondary relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0">
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-px h-px bg-primary/10 rounded-full"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              y: [0, -20, 0],
              opacity: [0, 0.3, 0],
            }}
            transition={{
              duration: 3 + Math.random() * 2,
              repeat: Infinity,
              delay: Math.random() * 3,
            }}
          />
        ))}
      </div>

      <div className="professional-container relative z-10 text-center">
        {/* Animated Janus Logo */}
        <motion.div
          initial={{ opacity: 0, scale: 0.5 }}
          whileInView={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1 }}
          viewport={{ once: true }}
          className="mb-12"
        >
          <div className="relative inline-block">
            {/* Logo particles building animation */}
            {[...Array(8)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute w-2 h-2 bg-primary rounded-full"
                style={{
                  left: `${20 + (i % 4) * 15}px`,
                  top: `${20 + Math.floor(i / 4) * 15}px`,
                }}
                initial={{ 
                  opacity: 0, 
                  scale: 0,
                  x: Math.random() * 100 - 50,
                  y: Math.random() * 100 - 50
                }}
                whileInView={{
                  opacity: 1,
                  scale: 1,
                  x: -(i % 4) * 15,
                  y: -Math.floor(i / 4) * 15
                }}
                transition={{
                  duration: 1.5,
                  delay: i * 0.1,
                  type: "spring",
                  stiffness: 100
                }}
                viewport={{ once: true }}
              />
            ))}
            
            <motion.div
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              transition={{ duration: 0.8, delay: 1.2 }}
              viewport={{ once: true }}
              className="w-20 h-20 bg-primary rounded-xl flex items-center justify-center relative z-10"
            >
              <Brain className="w-10 h-10 text-primary-foreground" />
            </motion.div>
          </div>
        </motion.div>

        <motion.h2
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
          viewport={{ once: true }}
          className="font-display text-4xl md:text-6xl text-foreground mb-8"
        >
          The Future of Property
          <br />
          <span className="text-primary">Is Intelligent</span>
        </motion.h2>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.5 }}
          viewport={{ once: true }}
          className="text-lg text-muted-foreground mb-12 max-w-2xl mx-auto"
        >
          Join the elite tier of real estate investors who leverage artificial intelligence
          to identify, analyze, and execute on opportunities before the market catches up.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.7 }}
          viewport={{ once: true }}
          className="space-y-6"
        >
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button 
            size="lg" 
            className="btn-professional text-base px-8 py-3"
          >
            Apply for Access
          </Button>
          <Button 
            size="lg" 
            className="btn-institutional text-base px-8 py-3"
          >
            Request Demo
          </Button>
          </div>
          
          <p className="text-sm text-muted-foreground">
            Limited access. Institutional investors only.
            <br />
            Minimum portfolio requirement: $1M+
          </p>
        </motion.div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 1, delay: 1 }}
          viewport={{ once: true }}
          className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8 pt-12 border-t border-border"
        >
          {[
            { value: "$2.4B+", label: "Assets Under Management" },
            { value: "94%", label: "Prediction Accuracy" },
            { value: "2.3x", label: "Average Portfolio Return" }
          ].map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 1.2 + index * 0.1 }}
              viewport={{ once: true }}
              className="text-center"
            >
              <div className="font-display text-2xl md:text-3xl text-primary mb-2">
                {stat.value}
              </div>
              <div className="text-muted-foreground text-sm">
                {stat.label}
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
};