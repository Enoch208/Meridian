"use client";

import { motion } from "motion/react";
import {
  AnalyticsUpIcon,
  Group01Icon,
  ShieldBlockchainIcon,
  Wallet01Icon,
} from "hugeicons-react";

import { AmbientGlow } from "@/components/ui/ambient-glow";
import { HoverEffect } from "@/components/ui/hover-effect";

const SCOUTS = [
  {
    title: "On-chain scout",
    description:
      "Reads mint and freeze authorities, contract age, and trap patterns. Disqualifies the obvious rugs before they ever reach the shortlist.",
    icon: <ShieldBlockchainIcon className="size-5" strokeWidth={1.5} />,
    examples: [
      "Mint authority revoked ✓",
      "Freeze authority renounced ✓",
      "Contract 9m old · flagged",
    ],
  },
  {
    title: "Liquidity scout",
    description:
      "Sizes the pool, checks what share is locked or burned, and reads the liquidity-to-mcap ratio. Filters illiquid and exit-rug setups.",
    icon: <Wallet01Icon className="size-5" strokeWidth={1.5} />,
    examples: [
      "LP 100% burned ✓",
      "Liq/mcap ratio healthy",
      "Thin liquidity · filtered out",
    ],
  },
  {
    title: "Momentum scout",
    description:
      "Watches the volume slope and buy/sell pressure. Surfaces early traction before it becomes obvious to everyone.",
    icon: <AnalyticsUpIcon className="size-5" strokeWidth={1.5} />,
    examples: [
      "Volume slope steepening",
      "Buy/sell pressure 3.2x",
      "Buy-side dominance confirmed",
    ],
  },
  {
    title: "Smart-money scout",
    description:
      "Overlays a curated whale watchlist on every candidate — distinct watchlist wallets that bought early raise the smart-money sub-score. The lead synthesizes all four into the ranked call.",
    icon: <Group01Icon className="size-5" strokeWidth={1.5} />,
    examples: [
      "Curated wallets cross-validated",
      "Early-buyer overlap detected",
      "Watchlist refreshes weekly",
    ],
  },
];

export function UseCasesGrid() {
  return (
    <section
      id="use-cases"
      className="relative overflow-hidden py-24 md:py-32"
    >
      <AmbientGlow position="top-left" intensity="subtle" size={800} />
      <AmbientGlow position="bottom-right" intensity="subtle" size={800} />

      <div className="relative z-10 mx-auto max-w-7xl px-6 md:px-10">
        <div className="mb-16 text-center">
          <motion.p
            initial={{ opacity: 0, y: 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-20%" }}
            transition={{ type: "spring", stiffness: 300, damping: 35 }}
            className="font-mono text-[10px] uppercase tracking-[0.22em] text-violet-400"
          >
            [ The Swarm ]
          </motion.p>
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-20%" }}
            transition={{ type: "spring", stiffness: 300, damping: 35, delay: 0.08 }}
            className="font-heading mx-auto mt-4 max-w-3xl text-4xl font-semibold leading-tight tracking-tight text-foreground md:text-5xl lg:text-6xl"
          >
            Four live scouts.
            <br />
            <span className="bg-gradient-to-r from-sky-300 via-violet-400 to-violet-600 bg-clip-text text-transparent">
              One ranked call.
            </span>
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-20%" }}
            transition={{ type: "spring", stiffness: 300, damping: 35, delay: 0.16 }}
            className="mx-auto mt-6 max-w-2xl text-base leading-relaxed text-muted-foreground"
          >
            Each scout watches a single signal and grades only what it can
            verify. A lead agent weighs the four live scouts and ranks the day&apos;s finds —
            multi-agent depth pointed at discovery, not judgment.
          </motion.p>
        </div>

        <HoverEffect items={SCOUTS} />
      </div>
    </section>
  );
}
