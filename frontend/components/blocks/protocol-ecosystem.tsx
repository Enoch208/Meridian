"use client";

import Image from "next/image";
import { motion } from "motion/react";
import {
  AnalyticsUpIcon,
  ArrowUpRight01Icon,
  CheckmarkCircle02Icon,
  FlashIcon,
} from "hugeicons-react";

import { AmbientGlow } from "@/components/ui/ambient-glow";
import { BentoGrid, BentoGridItem } from "@/components/ui/bento-grid";
import { MiniBarChart } from "@/components/ui/mini-bar-chart";
import { MiniLineChart } from "@/components/ui/mini-line-chart";
import { NumberTicker } from "@/components/ui/number-ticker";

// Deterministic seeded data — no hydration mismatch
function seededSeries(seed: number, length: number, base: number, range: number) {
  const values: number[] = [];
  for (let i = 0; i < length; i++) {
    const x = Math.sin(seed * (i + 1) * 12.9898) * 43758.5453;
    const noise = x - Math.floor(x);
    values.push(base + noise * range);
  }
  return values;
}

const SCAN_DATA = seededSeries(7, 28, 28, 72);
const CALLS_DATA = seededSeries(13, 20, 40, 60).map((v, i) => v + i * 2.4);

function StatEyebrow({ children }: { children: React.ReactNode }) {
  return (
    <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-muted-foreground">
      {children}
    </p>
  );
}

function TrendBadge({ value }: { value: string }) {
  return (
    <span className="inline-flex items-center gap-1 rounded-full border border-violet-500/30 bg-violet-500/10 px-2 py-0.5 font-mono text-[10px] font-semibold text-violet-300">
      <ArrowUpRight01Icon className="size-2.5" strokeWidth={3} />
      {value}
    </span>
  );
}

export function ProtocolEcosystem() {
  return (
    <section
      id="protocol"
      className="relative overflow-hidden py-24 md:py-32"
    >
      <AmbientGlow position="bottom-right" intensity="subtle" size={900} />

      <div className="relative z-10 mx-auto max-w-7xl px-6 md:px-10">
        {/* Section header */}
        <div className="mb-16 text-center">
          <motion.p
            initial={{ opacity: 0, y: 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-20%" }}
            transition={{ type: "spring", stiffness: 300, damping: 35 }}
            className="font-mono text-[10px] uppercase tracking-[0.22em] text-violet-400"
          >
            [ Track Record ]
          </motion.p>
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-20%" }}
            transition={{ type: "spring", stiffness: 300, damping: 35, delay: 0.08 }}
            className="font-heading mt-4 text-4xl font-semibold leading-tight tracking-tight text-foreground md:text-5xl lg:text-6xl"
          >
            A transparent track record.
            <br />
            <span className="bg-gradient-to-r from-sky-300 via-violet-400 to-violet-600 bg-clip-text text-transparent">
              Every call, logged.
            </span>
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-20%" }}
            transition={{ type: "spring", stiffness: 300, damping: 35, delay: 0.16 }}
            className="mx-auto mt-6 max-w-2xl text-base leading-relaxed text-muted-foreground"
          >
            One-shot tools have no memory. Meridian timestamps and scores every
            pick, then keeps the running scorecard public — wins and misses
            both. It&apos;s the credibility a paste-a-token verdict can&apos;t have.
          </motion.p>
        </div>

        <BentoGrid className="auto-rows-[minmax(12rem,18rem)]">
          {/* Card 1 — Launches scanned (col-span-2) */}
          <BentoGridItem
            index={0}
            className="md:col-span-2 md:row-span-1"
            header={
              <div className="flex h-full flex-col">
                <div className="flex items-start justify-between">
                  <div>
                    <StatEyebrow>Launches scanned · 30d</StatEyebrow>
                    <div className="mt-2 flex items-baseline gap-3">
                      <span className="font-heading text-4xl font-semibold tracking-tight text-foreground md:text-5xl">
                        <NumberTicker value={184920} />
                      </span>
                      <TrendBadge value="212%" />
                    </div>
                  </div>
                  <div className="inline-flex size-10 items-center justify-center rounded-xl border border-white/10 bg-white/5 text-violet-400">
                    <AnalyticsUpIcon className="size-5" strokeWidth={1.5} />
                  </div>
                </div>
                <div className="mt-auto h-24 w-full">
                  <MiniBarChart data={SCAN_DATA} height={96} />
                </div>
                <div className="mt-3 flex items-center justify-between font-mono text-[9px] uppercase tracking-[0.18em] text-muted-foreground">
                  <span>30d ago</span>
                  <span>15d ago</span>
                  <span>Today</span>
                </div>
              </div>
            }
          />

          {/* Card 2 — The scout swarm */}
          <BentoGridItem
            index={1}
            header={
              <div className="flex h-full flex-col justify-between">
                <div>
                  <StatEyebrow>The scout swarm</StatEyebrow>
                  <div className="mt-2 flex items-baseline gap-2">
                    <span className="font-heading text-4xl font-semibold tracking-tight text-foreground md:text-5xl">
                      <NumberTicker value={3} />
                    </span>
                    <span className="font-mono text-xs text-muted-foreground">
                      live scouts
                    </span>
                  </div>
                  <p className="mt-3 text-xs leading-relaxed text-muted-foreground">
                    Four live specialists watch one signal each; a lead synthesizes
                    them into the day&apos;s ranked shortlist. Smart-money overlays a
                    curated whale watchlist on every pick.
                  </p>
                </div>
                <div className="mt-6 flex -space-x-3">
                  {[
                    {
                      src: "/brand/avatars/detective.png",
                      alt: "On-chain scout",
                      bg: "from-violet-600 to-purple-900",
                    },
                    {
                      src: "/brand/avatars/woman-technologist.png",
                      alt: "Liquidity scout",
                      bg: "from-fuchsia-500 to-violet-800",
                    },
                    {
                      src: "/brand/avatars/man-scientist.png",
                      alt: "Momentum scout",
                      bg: "from-indigo-500 to-violet-900",
                    },
                    {
                      src: "/brand/avatars/ninja.png",
                      alt: "Smart-money scout",
                      bg: "from-violet-700 to-[#1E0A3C]",
                    },
                  ].map((avatar, i) => (
                    <div
                      key={avatar.src}
                      className={`relative size-11 overflow-hidden rounded-full border-2 border-[#0F1320] bg-gradient-to-br ${avatar.bg} ring-1 ring-white/15 transition-all duration-200 hover:z-10 hover:scale-110 hover:ring-violet-300/50 ${"roadmap" in avatar && avatar.roadmap ? "opacity-40 grayscale" : ""}`}
                      style={{ zIndex: 5 - i }}
                    >
                      {/* Subtle top-left specular highlight on the stage */}
                      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_30%_25%,rgba(255,255,255,0.25),transparent_55%)]" />
                      <Image
                        src={avatar.src}
                        alt={avatar.alt}
                        width={56}
                        height={56}
                        className="relative size-full scale-[1.35] object-contain object-bottom"
                      />
                    </div>
                  ))}
                  <div className="relative z-0 flex size-11 items-center justify-center rounded-full border-2 border-[#0F1320] bg-violet-500/15 font-mono text-[9px] font-semibold uppercase tracking-wide text-violet-300 ring-1 ring-violet-400/30">
                    Lead
                  </div>
                </div>
              </div>
            }
          />

          {/* Card 3 — Runs on Solana + Swarms */}
          <BentoGridItem
            index={2}
            header={
              <div className="flex h-full flex-col justify-between">
                <div>
                  <StatEyebrow>Runs on</StatEyebrow>
                  <div className="mt-2 flex items-center gap-3">
                    <div className="flex size-11 items-center justify-center rounded-xl border border-white/10 bg-white/5">
                      <Image
                        src="/brand/solana-mark.svg"
                        alt="Solana"
                        width={24}
                        height={24}
                        className="size-6"
                      />
                    </div>
                    <div>
                      <p className="font-heading text-lg font-semibold tracking-tight text-foreground">
                        Solana
                      </p>
                      <p className="font-mono text-[10px] uppercase tracking-[0.15em] text-muted-foreground">
                        Swarms Marketplace
                      </p>
                    </div>
                  </div>
                </div>
                <div>
                  <p className="text-xs leading-relaxed text-muted-foreground">
                    Tokenized prompt swarm, listed via Frenzy Mode. Hold $MRDN to
                    unlock the full daily shortlist.
                  </p>
                  <div className="mt-3 flex items-center gap-2">
                    <span className="size-1.5 animate-pulse rounded-full bg-violet-400" />
                    <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-violet-300">
                      Listed
                    </span>
                  </div>
                </div>
              </div>
            }
          />

          {/* Card 4 — Calls logged (col-span-2) */}
          <BentoGridItem
            index={3}
            className="md:col-span-2"
            header={
              <div className="flex h-full flex-col">
                <div className="flex items-start justify-between">
                  <div>
                    <StatEyebrow>Calls logged</StatEyebrow>
                    <div className="mt-2 flex items-baseline gap-3">
                      <span className="font-heading text-4xl font-semibold tracking-tight text-foreground md:text-5xl">
                        <NumberTicker value={1240} />
                      </span>
                      <span className="font-mono text-xs text-muted-foreground">
                        picks
                      </span>
                      <TrendBadge value="38%" />
                    </div>
                  </div>
                  <div className="inline-flex size-10 items-center justify-center rounded-xl border border-white/10 bg-white/5 text-violet-400">
                    <CheckmarkCircle02Icon className="size-5" strokeWidth={1.5} />
                  </div>
                </div>
                <div className="mt-auto h-24 w-full">
                  <MiniLineChart data={CALLS_DATA} height={96} />
                </div>
                <div className="mt-3 flex items-center justify-between font-mono text-[9px] uppercase tracking-[0.18em] text-muted-foreground">
                  <span>Daily cadence</span>
                  <span>Updated live</span>
                </div>
              </div>
            }
          />

          {/* Card 5 — Scored on rubric */}
          <BentoGridItem
            index={4}
            header={
              <div className="flex h-full flex-col justify-between">
                <div>
                  <StatEyebrow>Scored on rubric</StatEyebrow>
                  <div className="mt-2 flex items-baseline gap-2">
                    <span className="font-heading text-4xl font-semibold tracking-tight text-foreground md:text-5xl">
                      <NumberTicker value={100} />
                    </span>
                    <span className="font-mono text-xs text-muted-foreground">
                      % TRANSPARENT
                    </span>
                  </div>
                  <p className="mt-3 text-xs leading-relaxed text-muted-foreground">
                    Same rubric for every token. Unverifiable signals are marked
                    Unknown and down-weighted — never invented.
                  </p>
                </div>
                <div className="mt-6 space-y-1.5">
                  {[
                    { label: "Avg scan", value: "2.4s" },
                    { label: "Signals / token", value: "18" },
                    { label: "Refresh", value: "Daily" },
                  ].map((row) => (
                    <div
                      key={row.label}
                      className="flex items-center justify-between font-mono text-[10px] uppercase tracking-[0.15em]"
                    >
                      <span className="text-muted-foreground">
                        {row.label}
                      </span>
                      <span className="text-violet-300">{row.value}</span>
                    </div>
                  ))}
                </div>
              </div>
            }
          />

          {/* Card 6 — Latest calls live feed (fills bottom-right) */}
          <BentoGridItem
            index={5}
            className="md:col-span-2"
            header={
              <div className="flex h-full flex-col">
                <div className="flex items-start justify-between">
                  <StatEyebrow>Latest calls</StatEyebrow>
                  <div className="flex items-center gap-2">
                    <span className="relative flex size-1.5">
                      <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-60" />
                      <span className="relative inline-flex size-1.5 rounded-full bg-emerald-400" />
                    </span>
                    <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-emerald-300">
                      Live feed
                    </span>
                  </div>
                </div>

                <div className="mt-5 flex-1 space-y-3">
                  {[
                    {
                      ticker: "$NOVA",
                      time: "3s ago",
                      score: "87",
                      status: "surfaced",
                      icon: CheckmarkCircle02Icon,
                      accent: "text-emerald-300",
                      bg: "bg-emerald-500/10 border-emerald-500/30",
                    },
                    {
                      ticker: "$ORBT",
                      time: "18s ago",
                      score: "82",
                      status: "surfaced",
                      icon: CheckmarkCircle02Icon,
                      accent: "text-emerald-300",
                      bg: "bg-emerald-500/10 border-emerald-500/30",
                    },
                    {
                      ticker: "$HELIX",
                      time: "47s ago",
                      score: "74",
                      status: "watching",
                      icon: AnalyticsUpIcon,
                      accent: "text-violet-300",
                      bg: "bg-violet-500/10 border-violet-500/30",
                    },
                    {
                      ticker: "$ZEPH",
                      time: "1m ago",
                      score: "61",
                      status: "down-weighted",
                      icon: FlashIcon,
                      accent: "text-zinc-400",
                      bg: "bg-white/5 border-white/15",
                    },
                  ].map((row, i) => (
                    <motion.div
                      key={row.ticker}
                      initial={{ opacity: 0, x: -12 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      viewport={{ once: true, margin: "-10%" }}
                      transition={{
                        type: "spring",
                        stiffness: 260,
                        damping: 30,
                        delay: 0.15 + i * 0.08,
                      }}
                      className="flex items-center justify-between border-b border-white/5 pb-3 last:border-b-0 last:pb-0"
                    >
                      <div className="flex items-center gap-3">
                        <div
                          className={`flex size-8 items-center justify-center rounded-lg border ${row.bg}`}
                        >
                          <row.icon
                            className={`size-4 ${row.accent}`}
                            strokeWidth={1.8}
                          />
                        </div>
                        <div>
                          <div className="font-mono text-xs text-zinc-200">
                            {row.ticker}
                          </div>
                          <div className="mt-0.5 font-mono text-[10px] uppercase tracking-[0.12em] text-muted-foreground">
                            {row.time} · {row.status}
                          </div>
                        </div>
                      </div>
                      <div
                        className={`font-mono text-sm font-semibold ${row.accent}`}
                      >
                        {row.score}
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            }
          />
        </BentoGrid>
      </div>
    </section>
  );
}
