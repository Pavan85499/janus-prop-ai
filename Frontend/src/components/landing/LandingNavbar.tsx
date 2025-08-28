import { motion, useScroll, useTransform } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";

export const LandingNavbar = () => {
  const { scrollY } = useScroll();
  const opacity = useTransform(scrollY, [0, 100], [0, 1]);
  const backdropBlur = useTransform(scrollY, [0, 100], ["blur(0px)", "blur(20px)"]);

  return (
    <motion.nav
      style={{ opacity, backdropFilter: backdropBlur }}
      className="fixed top-0 left-0 right-0 z-50 border-b border-border/20"
    >
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
          className="font-display text-2xl font-bold"
        >
          Janus AI
        </motion.div>
        
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <Link to="/dashboard">
            <Button variant="outline" className="mr-4">
              Dashboard
            </Button>
          </Link>
          <Button className="bg-gradient-primary">
            Apply for Access
          </Button>
        </motion.div>
      </div>
    </motion.nav>
  );
};