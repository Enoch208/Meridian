"use client";

import { motion } from "motion/react";
import {
  AiBrain01Icon,
  CheckmarkCircle02Icon,
  DocumentValidationIcon,
} from "hugeicons-react";

import { AmbientGlow } from "@/components/ui/ambient-glow";
import { BorderBeam } from "@/components/ui/border-beam";

const PILLARS = [
  {
    eyebrow: "Pillar I",
    title: "The Scout Swarm",
    description:
      "Three live signal scouts read every new launch, each grading the one signal it owns. A lead agent synthesizes them into a single composite score against a transparent, fixed rubric. A smart-money scout joins in v1.5.",
    icon: <AiBrain01Icon className="size-5" strokeWidth={1.5} />,
    bullets: [
      "Three live scouts plus a ranking lead (v1 shipped)",
      "One transparent rubric, applied to every token",
      "Unverifiable signals down-weighted, never invented",
      "Framed 'worth investigating' — never 'buy'",
    ],
    accent: "from-violet-500/30 via-violet-600/10 to-transparent",
  },
  {
    eyebrow: "Pillar II",
    title: "The Track Record",
    description:
      "Every call is logged with a timestamp and the score it was given, and the scorecard stays public — wins and misses both. One-shot evaluation has no memory; this is the edge it can't copy.",
    icon: <DocumentValidationIcon className="size-5" strokeWidth={1.5} />,
    bullets: [
      "A public, running scorecard of every call",
      "Wins and misses both shown — honest by design",
      "Daily cadence gives a reason to come back",
      "Hold $MRDN to unlock the full real-time feed",
    ],
    accent: "from-sky-400/30 via-violet-500/10 to-transparent",
  },
];

export function ProtocolPillars() {
  return (
    <section className="relative overflow-hidden py-24 md:py-32">
      <AmbientGlow position="center" intensity="subtle" size={1000} />

      <div className="relative z-10 mx-auto max-w-7xl px-6 md:px-10">
        <div className="mb-16 text-center">
          <motion.p
            initial={{ opacity: 0, y: 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-20%" }}
            transition={{ type: "spring", stiffness: 300, damping: 35 }}
            className="font-mono text-[10px] uppercase tracking-[0.22em] text-violet-400"
          >
            [ The Moat ]
          </motion.p>
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-20%" }}
            transition={{ type: "spring", stiffness: 300, damping: 35, delay: 0.08 }}
            className="font-heading mx-auto mt-4 max-w-3xl text-4xl font-semibold leading-tight tracking-tight text-foreground md:text-5xl lg:text-6xl"
          >
            Two pillars.
            <br />
            <span className="bg-gradient-to-r from-sky-300 via-violet-400 to-violet-600 bg-clip-text text-transparent">
              One honest edge.
            </span>
          </motion.h2>
        </div>

        <div className="grid gap-8 md:grid-cols-2">
          {PILLARS.map((pillar, i) => (
            <motion.div
              key={pillar.title}
              initial={{ opacity: 0, y: 32 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-15%" }}
              transition={{
                type: "spring",
                stiffness: 300,
                damping: 35,
                delay: i * 0.12,
              }}
              className="group relative overflow-hidden rounded-3xl border border-white/10 bg-[#0F1320] p-8 md:p-10"
            >
              {/* Accent glow */}
              <div
                className={`pointer-events-none absolute -top-24 -right-24 size-64 rounded-full bg-gradient-to-br ${pillar.accent} blur-3xl`}
              />
              {/* Border beam */}
              <BorderBeam
                size={120}
                duration={12}
                delay={i * 2}
                colorFrom="#8B5CF6"
                colorTo="#2E1065"
              />

              <div className="relative z-10">
                <div className="flex items-center gap-3">
                  <div className="inline-flex size-11 items-center justify-center rounded-xl border border-violet-500/30 bg-violet-500/10 text-violet-300">
                    {pillar.icon}
                  </div>
                  <span className="font-mono text-[10px] uppercase tracking-[0.22em] text-muted-foreground">
                    {pillar.eyebrow}
                  </span>
                </div>

                <h3 className="font-heading mt-6 text-3xl font-semibold leading-tight tracking-tight text-foreground md:text-4xl">
                  {pillar.title}
                </h3>
                <p className="mt-4 text-base leading-relaxed text-muted-foreground">
                  {pillar.description}
                </p>

                <ul className="mt-8 space-y-3">
                  {pillar.bullets.map((bullet) => (
                    <li
                      key={bullet}
                      className="flex items-start gap-3 text-sm text-zinc-300"
                    >
                      <CheckmarkCircle02Icon
                        className="mt-0.5 size-4 shrink-0 text-violet-400"
                        strokeWidth={1.8}
                      />
                      <span>{bullet}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
