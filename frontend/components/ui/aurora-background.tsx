"use client";

import { cn } from "@/lib/utils";
import { motion } from "motion/react";
import type { ReactNode } from "react";

interface AuroraBackgroundProps {
  children: ReactNode;
  className?: string;
  showRadialGradient?: boolean;
}

export function AuroraBackground({
  children,
  className,
  showRadialGradient = true,
}: AuroraBackgroundProps) {
  return (
    <div
      className={cn(
        "relative flex min-h-screen flex-col items-center justify-center bg-[#0A0A0A] text-zinc-50 transition-bg",
        className
      )}
    >
      <div className="absolute inset-0 overflow-hidden">
        <div
          className={cn(
            "pointer-events-none absolute -inset-[10px] opacity-40 blur-[10px] filter will-change-transform [--aurora:repeating-linear-gradient(100deg,#2E1065_10%,#4C1D95_15%,#7C3AED_20%,#8B5CF6_25%,#2E1065_30%)] [background-image:var(--aurora)] [background-position:50%_50%,50%_50%] [background-size:300%,_200%]",
            showRadialGradient &&
              "[mask-image:radial-gradient(ellipse_at_100%_0%,black_10%,transparent_70%)]"
          )}
        >
          <motion.div
            className="absolute inset-0 [background-image:inherit] [background-position:inherit] [background-size:inherit]"
            animate={{
              backgroundPosition: ["50% 50%, 50% 50%", "350% 50%, 350% 50%"],
            }}
            transition={{
              duration: 60,
              repeat: Infinity,
              ease: "linear",
            }}
          />
        </div>
      </div>
      {children}
    </div>
  );
}
