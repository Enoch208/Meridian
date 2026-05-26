"use client";

import { ReactNode, useCallback } from "react";
import { motion, useMotionTemplate, useMotionValue } from "motion/react";

import { cn } from "@/lib/utils";

interface GlowCardProps {
  children: ReactNode;
  className?: string;
  hoverGlow?: boolean;
  innerHighlight?: boolean;
  padding?: "sm" | "md" | "lg" | "none";
}

const PADDING_CLASSES: Record<NonNullable<GlowCardProps["padding"]>, string> = {
  none: "",
  sm: "p-4",
  md: "p-6",
  lg: "p-8",
};

export function GlowCard({
  children,
  className,
  hoverGlow = true,
  innerHighlight = true,
  padding = "md",
}: GlowCardProps) {
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  const handleMouseMove = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      if (!hoverGlow) return;
      const { left, top } = e.currentTarget.getBoundingClientRect();
      mouseX.set(e.clientX - left);
      mouseY.set(e.clientY - top);
    },
    [mouseX, mouseY, hoverGlow],
  );

  return (
    <div
      onMouseMove={handleMouseMove}
      className={cn(
        "group/glow relative overflow-hidden rounded-2xl border border-white/10 bg-[#0F1320] transition-colors duration-200 hover:border-white/20",
        PADDING_CLASSES[padding],
        className,
      )}
    >
      {innerHighlight && (
        <div
          aria-hidden
          className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-violet-500/40 to-transparent"
        />
      )}
      {hoverGlow && (
        <motion.div
          aria-hidden
          className="pointer-events-none absolute -inset-px z-0 opacity-0 transition-opacity duration-300 group-hover/glow:opacity-100"
          style={{
            background: useMotionTemplate`radial-gradient(500px circle at ${mouseX}px ${mouseY}px, rgba(139, 92, 246, 0.1), transparent 60%)`,
          }}
        />
      )}
      <div className="relative z-10">{children}</div>
    </div>
  );
}
