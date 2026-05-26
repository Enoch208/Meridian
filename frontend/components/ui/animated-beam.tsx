"use client";

import { cn } from "@/lib/utils";
import { motion } from "motion/react";

export function AnimatedBeam({
  className,
  delay = 0,
}: {
  className?: string;
  delay?: number;
}) {
  return (
    <div className={cn("relative", className)}>
      <motion.div
        className="absolute inset-0 rounded-2xl"
        style={{
          background:
            "linear-gradient(90deg, transparent, rgba(139, 92, 246, 0.3), transparent)",
        }}
        animate={{
          x: ["-100%", "200%"],
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          delay,
          ease: "linear",
        }}
      />
    </div>
  );
}
