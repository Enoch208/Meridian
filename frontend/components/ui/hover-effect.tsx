"use client";

import { ReactNode, useState } from "react";
import { AnimatePresence, motion } from "motion/react";

import { cn } from "@/lib/utils";

export interface HoverEffectItem {
  title: string;
  description: string;
  icon?: ReactNode;
  examples?: string[];
  badge?: string;
}

export function HoverEffect({
  items,
  className,
}: {
  items: HoverEffectItem[];
  className?: string;
}) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  return (
    <div
      className={cn(
        "grid grid-cols-1 gap-6 md:grid-cols-2",
        className,
      )}
    >
      {items.map((item, idx) => (
        <div
          key={item.title}
          className="group relative block h-full w-full p-2"
          onMouseEnter={() => setHoveredIndex(idx)}
          onMouseLeave={() => setHoveredIndex(null)}
        >
          <AnimatePresence>
            {hoveredIndex === idx && (
              <motion.span
                className="absolute inset-0 block h-full w-full rounded-2xl bg-violet-500/10"
                layoutId="hoverBackground"
                initial={{ opacity: 0 }}
                animate={{
                  opacity: 1,
                  transition: { duration: 0.15 },
                }}
                exit={{
                  opacity: 0,
                  transition: { duration: 0.15, delay: 0.12 },
                }}
              />
            )}
          </AnimatePresence>
          <Card roadmap={!!item.badge}>
            <CardIcon>{item.icon}</CardIcon>
            <CardTitleRow title={item.title} badge={item.badge} />
            <CardDescription>{item.description}</CardDescription>
            {item.examples && item.examples.length > 0 && (
              <div className="mt-6 border-t border-white/10 pt-4">
                <p className="mb-2 font-mono text-[10px] uppercase tracking-[0.2em] text-muted-foreground">
                  {item.badge ? "Planned capability" : "Example"}
                </p>
                <ul className="space-y-1.5">
                  {item.examples.map((ex) => (
                    <li
                      key={ex}
                      className="flex items-center gap-2 font-mono text-xs text-zinc-500"
                    >
                      <span className="size-1 rounded-full bg-zinc-600/60" />
                      {ex}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </Card>
        </div>
      ))}
    </div>
  );
}

function Card({ children, roadmap }: { children: ReactNode; roadmap?: boolean }) {
  return (
    <div className={`relative z-10 h-full w-full overflow-hidden rounded-2xl border bg-[#0F1320] p-8 transition-colors ${roadmap ? "border-white/5 opacity-70 group-hover:border-zinc-700/40" : "border-white/10 group-hover:border-violet-500/30"}`}>
      <div className="relative z-10">{children}</div>
    </div>
  );
}

function CardIcon({ children }: { children: ReactNode }) {
  if (!children) return null;
  return (
    <div className="mb-5 inline-flex size-11 items-center justify-center rounded-xl border border-white/10 bg-white/5 text-violet-400 transition-colors group-hover:border-violet-500/30 group-hover:text-violet-300">
      {children}
    </div>
  );
}

function CardTitleRow({ title, badge }: { title: ReactNode; badge?: string }) {
  return (
    <div className="flex items-center gap-2.5">
      <h3 className="font-heading text-xl font-semibold leading-tight tracking-tight text-foreground">
        {title}
      </h3>
      {badge && (
        <span className="inline-flex items-center rounded-full border border-zinc-700/60 bg-zinc-800/60 px-2 py-0.5 font-mono text-[9px] uppercase tracking-[0.18em] text-zinc-500">
          {badge}
        </span>
      )}
    </div>
  );
}

function CardDescription({ children }: { children: ReactNode }) {
  return (
    <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
      {children}
    </p>
  );
}
