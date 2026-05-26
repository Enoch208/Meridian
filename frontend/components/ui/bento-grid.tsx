"use client";

import { ReactNode } from "react";
import { motion } from "motion/react";

import { cn } from "@/lib/utils";

export function BentoGrid({
  className,
  children,
}: {
  className?: string;
  children: ReactNode;
}) {
  return (
    <div
      className={cn(
        "mx-auto grid max-w-7xl grid-cols-1 gap-4 md:auto-rows-[18rem] md:grid-cols-3",
        className,
      )}
    >
      {children}
    </div>
  );
}

export function BentoGridItem({
  className,
  title,
  description,
  header,
  icon,
  index = 0,
}: {
  className?: string;
  title?: ReactNode;
  description?: ReactNode;
  header?: ReactNode;
  icon?: ReactNode;
  index?: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-15%" }}
      transition={{
        type: "spring",
        stiffness: 300,
        damping: 35,
        delay: index * 0.08,
      }}
      className={cn(
        "group relative flex flex-col justify-between overflow-hidden rounded-2xl border border-white/10 bg-[#0F1320] p-6 transition-colors duration-200 hover:border-white/20",
        className,
      )}
    >
      <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-violet-500/40 to-transparent" />
      {header && <div className="relative z-10 mb-4 flex-1">{header}</div>}
      <div className="relative z-10">
        {icon && <div className="mb-3 text-violet-400">{icon}</div>}
        {title && (
          <h3 className="font-heading text-xl font-semibold leading-tight tracking-tight text-foreground">
            {title}
          </h3>
        )}
        {description && (
          <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
            {description}
          </p>
        )}
      </div>
    </motion.div>
  );
}
