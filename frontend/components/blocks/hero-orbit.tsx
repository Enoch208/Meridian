"use client";

import Image from "next/image";
import Link from "next/link";
import { motion } from "motion/react";
import { ArrowUpRight01Icon } from "hugeicons-react";

import { AmbientGlow } from "@/components/ui/ambient-glow";
import { MeridianMark } from "@/components/ui/meridian-mark";
import { BorderBeam } from "@/components/ui/border-beam";
import { Button } from "@/components/ui/button";

const spring = { type: "spring" as const, stiffness: 400, damping: 30 };

/* Blips on the scope — a few "found" with a target-lock + ticker, the rest
   dim noise. Positions are percentages within the square scope. */
type Blip = {
  top: string;
  left: string;
  found?: boolean;
  ticker?: string;
  tone?: "violet" | "emerald";
  delay?: number;
};

const BLIPS: Blip[] = [
  { top: "27%", left: "66%", found: true, ticker: "$NOVA", tone: "emerald", delay: 0 },
  { top: "63%", left: "31%", found: true, ticker: "$ORBT", tone: "violet", delay: 0.6 },
  { top: "70%", left: "63%", found: true, ticker: "$HELIX", tone: "violet", delay: 1.1 },
  { top: "20%", left: "40%", delay: 0.3 },
  { top: "48%", left: "19%", delay: 0.9 },
  { top: "80%", left: "44%", delay: 1.4 },
  { top: "34%", left: "82%", delay: 1.8 },
];

function Blip({ blip }: { blip: Blip }) {
  if (!blip.found) {
    return (
      <motion.span
        aria-hidden
        initial={{ opacity: 0 }}
        animate={{ opacity: [0.15, 0.5, 0.15] }}
        transition={{ duration: 3.5, repeat: Infinity, delay: blip.delay ?? 0 }}
        className="absolute size-1 rounded-full bg-zinc-400"
        style={{ top: blip.top, left: blip.left }}
      />
    );
  }

  const dot = blip.tone === "emerald" ? "bg-emerald-400" : "bg-violet-400";
  const ring = blip.tone === "emerald" ? "border-emerald-400/50" : "border-violet-400/50";
  const text = blip.tone === "emerald" ? "text-emerald-300" : "text-violet-300";

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.6 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ ...spring, delay: 0.8 + (blip.delay ?? 0) }}
      className="absolute flex items-center gap-1.5"
      style={{ top: blip.top, left: blip.left }}
    >
      <span className="relative flex size-2">
        <span className={`absolute inline-flex size-full animate-ping rounded-full ${dot} opacity-60`} />
        <span className={`relative inline-flex size-2 rounded-full ${dot}`} />
      </span>
      {/* target-lock ring */}
      <span className={`pointer-events-none absolute -left-1 -top-1 size-4 rounded-full border ${ring}`} />
      <span className={`font-mono text-[9px] font-medium tracking-wide ${text}`}>
        {blip.ticker}
      </span>
    </motion.div>
  );
}

function RadarScope() {
  return (
    <div className="relative mx-auto aspect-square w-full max-w-[400px] sm:max-w-[440px] lg:max-w-[520px]">
      {/* Ambient bloom behind the scope */}
      <div className="pointer-events-none absolute inset-[8%] rounded-full bg-[radial-gradient(circle,rgba(139,92,246,0.22),transparent_68%)] blur-2xl" />

      {/* Concentric range rings */}
      {["inset-0", "inset-[14%]", "inset-[30%]", "inset-[46%]"].map((inset) => (
        <div
          key={inset}
          aria-hidden
          className={`absolute ${inset} rounded-full border border-white/[0.07]`}
        />
      ))}

      {/* Crosshair */}
      <div aria-hidden className="absolute left-1/2 top-0 h-full w-px -translate-x-1/2 bg-white/[0.05]" />
      <div aria-hidden className="absolute top-1/2 left-0 h-px w-full -translate-y-1/2 bg-white/[0.05]" />

      {/* Rotating sweep wedge */}
      <motion.div
        aria-hidden
        className="absolute inset-0 rounded-full"
        style={{
          background:
            "conic-gradient(from 0deg, transparent 0deg, rgba(139,92,246,0) 36deg, rgba(139,92,246,0.30) 78deg, rgba(167,139,250,0.55) 90deg, transparent 92deg)",
          maskImage: "radial-gradient(circle, black 70%, transparent 71%)",
          WebkitMaskImage: "radial-gradient(circle, black 70%, transparent 71%)",
        }}
        animate={{ rotate: 360 }}
        transition={{ duration: 7, ease: "linear", repeat: Infinity }}
      />

      {/* Blips */}
      {BLIPS.map((blip, i) => (
        <Blip key={i} blip={blip} />
      ))}

      {/* Center mark */}
      <div className="absolute left-1/2 top-1/2 flex size-[26%] -translate-x-1/2 -translate-y-1/2 items-center justify-center">
        <div className="pointer-events-none absolute size-[180%] animate-pulse-glow rounded-full bg-[radial-gradient(circle,rgba(167,139,250,0.4),transparent_70%)] blur-xl" />
        <div className="relative size-full">
          <MeridianMark size={160} animated className="h-full w-full" />
          <div className="pointer-events-none absolute inset-0 overflow-hidden rounded-[26%]">
            <BorderBeam size={120} duration={7} colorFrom="#DDD6FE" colorTo="#1E2B4A" borderWidth={1.5} />
          </div>
        </div>
      </div>
    </div>
  );
}

export function HeroOrbit() {
  return (
    <section className="relative overflow-hidden pt-[calc(4rem+1.5rem)] pb-16 sm:pt-[calc(4rem+2rem)] sm:pb-20 md:pt-28 md:pb-28">
      {/* Ambient backdrops */}
      <AmbientGlow position="top" intensity="strong" size={1100} />
      <AmbientGlow position="top-right" intensity="subtle" size={760} />

      {/* Grid overlay mask */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 opacity-40 [mask-image:radial-gradient(ellipse_at_top,black_30%,transparent_70%)]"
        style={{
          backgroundImage:
            "linear-gradient(to right, rgba(255,255,255,0.04) 1px, transparent 1px), linear-gradient(to bottom, rgba(255,255,255,0.04) 1px, transparent 1px)",
          backgroundSize: "64px 64px",
        }}
      />

      <div className="relative z-10 mx-auto max-w-7xl px-6 md:px-10">
        <div className="grid items-center gap-12 lg:grid-cols-[1.12fr_0.88fr] lg:gap-8">
          {/* ── LEFT — copy ─────────────────────────────────── */}
          <div className="text-center lg:text-left">
            {/* Eyebrow */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ ...spring, delay: 0.05 }}
              className="inline-flex items-center gap-2 rounded-full border border-violet-500/30 bg-violet-500/10 px-3.5 py-1.5 sm:px-4"
            >
              <span className="size-1.5 animate-pulse rounded-full bg-violet-400" />
              <span className="font-mono text-[9px] uppercase tracking-[0.22em] text-violet-300 sm:text-[10px]">
                Multi-agent discovery · Solana
              </span>
            </motion.div>

            {/* Headline */}
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ ...spring, delay: 0.12 }}
              className="font-heading mx-auto mt-5 max-w-2xl text-[32px] font-semibold leading-[0.98] tracking-tight text-foreground min-[380px]:text-[38px] sm:mt-7 sm:text-5xl md:text-6xl lg:mx-0 lg:text-[58px]"
            >
              <span className="lg:whitespace-nowrap">The discovery layer</span>
              <br />
              <span className="bg-gradient-to-r from-sky-200 via-violet-400 to-violet-600 bg-clip-text text-transparent">
                for Solana
                <br />
                launches.
              </span>
            </motion.h1>

            {/* Subhead — tightened */}
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ ...spring, delay: 0.18 }}
              className="mx-auto mt-5 max-w-md text-base leading-relaxed text-muted-foreground sm:mt-6 md:text-lg lg:mx-0"
            >
              Hundreds of tokens launch on Solana daily. The scout swarm finds
              the few worth investigating — and logs every call in public.
            </motion.p>

            {/* CTAs */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ ...spring, delay: 0.24 }}
              className="mt-7 flex flex-wrap items-center justify-center gap-3 sm:mt-8 lg:justify-start"
            >
              <motion.div whileHover={{ scale: 0.97 }} whileTap={{ scale: 0.94 }}>
                <Link href="/demo">
                  <Button variant="violet" size="pill">
                    See Today&apos;s Picks
                    <ArrowUpRight01Icon className="size-4" strokeWidth={2.2} />
                  </Button>
                </Link>
              </motion.div>
              <motion.div whileHover={{ scale: 0.97 }} whileTap={{ scale: 0.94 }}>
                <Link href="/#lifecycle">
                  <Button variant="outline" size="pill">
                    How It Works
                  </Button>
                </Link>
              </motion.div>
            </motion.div>

            {/* Trust row */}
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ ...spring, delay: 0.36 }}
              className="mx-auto mt-7 flex max-w-xl flex-wrap items-center justify-center gap-x-5 gap-y-2 font-mono text-[9px] uppercase tracking-[0.18em] text-muted-foreground sm:mt-8 sm:gap-x-6 sm:text-[10px] sm:tracking-[0.2em] lg:mx-0 lg:justify-start"
            >
              <span className="flex items-center gap-1.5 sm:gap-2">
                <Image
                  src="/brand/solana-mark.svg"
                  alt="Solana"
                  width={14}
                  height={14}
                  className="size-3 sm:size-3.5"
                />
                Built on Solana
              </span>
              <span className="inline-block size-1 rounded-full bg-white/20" />
              <span>
                <span className="text-violet-300">3</span> live scouts
              </span>
              <span className="inline-block size-1 rounded-full bg-white/20" />
              <span>Public track record</span>
            </motion.div>
          </div>

          {/* ── RIGHT — radar scope ─────────────────────────── */}
          <motion.div
            initial={{ opacity: 0, scale: 0.94 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ ...spring, delay: 0.3 }}
            className="relative"
          >
            <RadarScope />
          </motion.div>
        </div>
      </div>
    </section>
  );
}
