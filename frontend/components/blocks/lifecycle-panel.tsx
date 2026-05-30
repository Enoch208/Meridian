"use client";

import { motion, AnimatePresence } from "motion/react";
import { Meteors } from "@/components/ui/meteors";

// Tight spring for child element staggers within a state panel
const spring = { type: "spring" as const, stiffness: 400, damping: 30 };

// Softer spring for state-to-state transitions — feels cushioned, not abrupt
const panelSpring = {
  type: "spring" as const,
  stiffness: 180,
  damping: 28,
  mass: 0.9,
};

/* ─────────────────────────────────────────────
   STATE 1: The Scan — a candidate being ingested
   ───────────────────────────────────────────── */
function StateScan() {
  const lines = [
    { indent: 0, text: "{" },
    { indent: 1, key: "ticker", value: '"$NOVA"' },
    { indent: 1, key: "pair_age", value: '"14m"' },
    { indent: 1, key: "liquidity", value: '"$82,400"' },
    { indent: 1, key: "lp_locked", value: '"100%"' },
    { indent: 1, key: "holders", value: "412" },
    { indent: 1, key: "mint_authority", value: '"revoked"' },
    { indent: 0, text: "}" },
  ];

  return (
    <div className="flex h-full flex-col p-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={spring}
        className="mb-4 flex items-center gap-2"
      >
        <span className="relative flex h-1.5 w-1.5">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-amber-400 opacity-75" />
          <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-amber-400" />
        </span>
        <span className="font-mono text-[10px] uppercase tracking-widest text-amber-400">
          Scanning_Launches
        </span>
      </motion.div>

      {/* JSON output */}
      <div className="flex-1 font-mono text-xs leading-8">
        {lines.map((line, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: 12 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ ...spring, delay: i * 0.08 }}
          >
            {"  ".repeat(line.indent)}
            {line.key ? (
              <>
                <span className="text-zinc-500">&quot;</span>
                <span className="text-violet-300">{line.key}</span>
                <span className="text-zinc-500">&quot;</span>
                <span className="text-zinc-600">: </span>
                <span className="text-amber-300">{line.value}</span>
                {i < lines.length - 2 && (
                  <span className="text-zinc-600">,</span>
                )}
              </>
            ) : (
              <span className="text-zinc-500">{line.text}</span>
            )}
          </motion.div>
        ))}
      </div>

      {/* Footer */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
        className="mt-4 border-t border-white/5 pt-4"
      >
        <span className="font-mono text-[10px] text-zinc-600">
          Pulling new Solana pairs → candidate stream...
        </span>
      </motion.div>
    </div>
  );
}

/* ─────────────────────────────────────────────
   STATE 2: The Score — scouts grade the rubric
   ───────────────────────────────────────────── */
function StateScore() {
  const scouts = [
    { label: "On-chain", value: "PASS · mint revoked", color: "text-emerald-300" },
    { label: "Liquidity", value: "PASS · LP 100% locked", color: "text-emerald-300" },
    { label: "Momentum", value: "↑ buy/sell 3.2x · slope+", color: "text-violet-300" },
    { label: "Smart-money", value: "watchlist overlay · 2 hits", color: "text-emerald-300" },
  ];

  return (
    <div className="flex h-full flex-col p-8">
      {/* Status badge */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={spring}
        className="mb-8 inline-flex w-fit items-center gap-2 rounded-full border border-violet-500/30 bg-violet-500/10 px-3 py-1"
      >
        <span className="relative flex h-1.5 w-1.5">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-violet-400 opacity-75" />
          <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-violet-400" />
        </span>
        <span className="font-mono text-[10px] uppercase tracking-widest text-violet-300">
          Status: Scoring_$NOVA
        </span>
      </motion.div>

      {/* Scout sub-scores */}
      <div className="flex-1 space-y-4">
        {scouts.map((scout, i) => (
          <motion.div
            key={scout.label}
            initial={{ opacity: 0, x: 16 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ ...spring, delay: 0.1 + i * 0.08 }}
            className="flex items-center justify-between border-b border-white/5 pb-4"
          >
            <span className="font-mono text-[10px] uppercase tracking-widest text-zinc-600">
              {scout.label}
            </span>
            <span className={`font-mono text-xs ${scout.color}`}>
              {scout.value}
            </span>
          </motion.div>
        ))}
      </div>

      {/* Composite */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="mt-4 border-t border-white/5 pt-4"
      >
        <div className="flex items-center justify-between">
          <span className="font-mono text-[10px] text-zinc-600">
            Composite score
          </span>
          <span className="font-mono text-sm font-semibold text-violet-300">
            87 / 100
          </span>
        </div>
        <div className="mt-2 flex items-center justify-between">
          <span className="font-mono text-[10px] text-zinc-600">Rubric</span>
          <span className="font-mono text-[10px] text-zinc-500">
            v3 · synthesized by lead
          </span>
        </div>
      </motion.div>
    </div>
  );
}

/* ─────────────────────────────────────────────
   STATE 3: The Call — ranked & logged
   ───────────────────────────────────────────── */
function StateCall() {
  return (
    <div className="relative flex h-full flex-col overflow-hidden p-8">
      {/* Violet pulse burst behind content */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-1/2 top-1/2 size-[420px] -translate-x-1/2 -translate-y-1/2 animate-pulse-glow rounded-full bg-[radial-gradient(circle,rgba(139,92,246,0.25)_0%,rgba(124,58,237,0.08)_40%,transparent_70%)] mix-blend-screen" />
      </div>
      <Meteors count={8} />

      {/* Status badge */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={spring}
        className="relative z-10 mb-8 inline-flex w-fit items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1"
      >
        <span className="relative flex h-1.5 w-1.5">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
          <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-emerald-400" />
        </span>
        <span className="font-mono text-[10px] uppercase tracking-widest text-emerald-300">
          Status: Logged_Call
        </span>
      </motion.div>

      {/* Pick summary */}
      <div className="relative z-10 flex-1 space-y-4">
        {[
          { label: "Rank", value: "#1 of today" },
          { label: "Token", value: "$NOVA" },
          { label: "Composite", value: "87 / 100" },
          { label: "Why it surfaced", value: "LP locked + buy pressure" },
          { label: "Standout risk", value: "Only 14m old" },
        ].map((field, i) => (
          <motion.div
            key={field.label}
            initial={{ opacity: 0, x: 16 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ ...spring, delay: 0.1 + i * 0.08 }}
            className="flex items-center justify-between border-b border-white/5 pb-4"
          >
            <span className="font-mono text-[10px] uppercase tracking-widest text-zinc-600">
              {field.label}
            </span>
            <span
              className={`font-mono text-xs ${
                field.label === "Composite"
                  ? "text-emerald-300"
                  : "text-zinc-400"
              }`}
            >
              {field.value}
            </span>
          </motion.div>
        ))}
      </div>

      {/* Logged */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
        className="relative z-10 mt-4 border-t border-white/5 pt-4"
      >
        <div className="flex items-center justify-between">
          <span className="font-mono text-[10px] text-zinc-600">
            Track record
          </span>
          <span className="font-mono text-[10px] text-emerald-300">
            Logged — 2026-05-26 14:02 UTC
          </span>
        </div>
      </motion.div>
    </div>
  );
}

/* ─────────────────────────────────────────────
   TRAFFIC LIGHT — single macOS window control
   ───────────────────────────────────────────── */
function TrafficLight({ color }: { color: "red" | "yellow" | "green" }) {
  const palette = {
    red: {
      bg: "#ff5f57",
      ring: "#e0443e",
      highlight: "rgba(255, 200, 195, 0.6)",
    },
    yellow: {
      bg: "#febc2e",
      ring: "#dea123",
      highlight: "rgba(255, 230, 160, 0.6)",
    },
    green: {
      bg: "#28c840",
      ring: "#1aab29",
      highlight: "rgba(170, 240, 180, 0.6)",
    },
  }[color];

  return (
    <span
      aria-hidden
      className="relative block size-3 rounded-full"
      style={{
        background: palette.bg,
        boxShadow: `
          0 0 0 0.5px ${palette.ring},
          inset 0 0.5px 0 ${palette.highlight},
          inset 0 -0.5px 0 rgba(0, 0, 0, 0.25)
        `,
      }}
    />
  );
}

/* ─────────────────────────────────────────────
   LIFECYCLE PANEL — scroll-driven state machine
   ───────────────────────────────────────────── */
export function LifecyclePanel({
  activeState,
}: {
  activeState: 0 | 1 | 2;
}) {
  const statusLabel =
    activeState === 0 ? "scanning" : activeState === 1 ? "scoring" : "logged";
  const statusDotClass =
    activeState === 0
      ? "bg-amber-400"
      : activeState === 1
        ? "bg-violet-400"
        : "bg-emerald-400";

  return (
    <div className="relative">
      {/* Outer atmospheric glow — gives the terminal a floating feel */}
      <div
        aria-hidden
        className="pointer-events-none absolute -inset-8 rounded-[32px] bg-[radial-gradient(60%_50%_at_50%_50%,rgba(139,92,246,0.18),transparent_75%)] blur-2xl"
      />

      {/* Terminal body */}
      <motion.div
        layout
        transition={panelSpring}
        className="relative overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-b from-[#10131F] via-[#0B0D18] to-[#070912] shadow-[0_1px_0_rgba(255,255,255,0.06)_inset,0_24px_48px_-24px_rgba(0,0,0,0.8),0_40px_80px_-32px_rgba(139,92,246,0.35)] ring-1 ring-white/5"
      >
        {/* Top inner highlight line — simulates glass bevel */}
        <div
          aria-hidden
          className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent"
        />

        {/* Title bar */}
        <div className="relative flex h-10 items-center border-b border-white/5 bg-gradient-to-b from-[#161A2A] to-[#121524] px-4">
          {/* Traffic lights */}
          <div className="flex items-center gap-2">
            <TrafficLight color="red" />
            <TrafficLight color="yellow" />
            <TrafficLight color="green" />
          </div>

          {/* Centered filename */}
          <div className="pointer-events-none absolute inset-x-0 flex justify-center">
            <span className="font-mono text-[11px] tracking-wide text-zinc-500">
              meridian-pipeline
            </span>
          </div>

          {/* Right — live state indicator */}
          <div className="ml-auto flex items-center gap-2">
            <span className="relative flex size-1.5">
              <span
                className={`absolute inline-flex h-full w-full animate-ping rounded-full ${statusDotClass} opacity-60`}
              />
              <span
                className={`relative inline-flex size-1.5 rounded-full ${statusDotClass}`}
              />
            </span>
            <motion.span
              key={statusLabel}
              initial={{ opacity: 0, y: -4 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.25 }}
              className="font-mono text-[10px] uppercase tracking-[0.18em] text-zinc-500"
            >
              {statusLabel}
            </motion.span>
          </div>
        </div>

        {/* State content */}
        <div className="relative h-[480px]">
          <AnimatePresence mode="popLayout" initial={false}>
            {activeState === 0 && (
              <motion.div
                key="scan"
                initial={{ opacity: 0, y: 24, scale: 0.985, filter: "blur(6px)" }}
                animate={{ opacity: 1, y: 0, scale: 1, filter: "blur(0px)" }}
                exit={{ opacity: 0, y: -24, scale: 0.985, filter: "blur(6px)" }}
                transition={panelSpring}
                className="absolute inset-0"
              >
                <StateScan />
              </motion.div>
            )}
            {activeState === 1 && (
              <motion.div
                key="score"
                initial={{ opacity: 0, y: 24, scale: 0.985, filter: "blur(6px)" }}
                animate={{ opacity: 1, y: 0, scale: 1, filter: "blur(0px)" }}
                exit={{ opacity: 0, y: -24, scale: 0.985, filter: "blur(6px)" }}
                transition={panelSpring}
                className="absolute inset-0"
              >
                <StateScore />
              </motion.div>
            )}
            {activeState === 2 && (
              <motion.div
                key="call"
                initial={{ opacity: 0, y: 24, scale: 0.985, filter: "blur(6px)" }}
                animate={{ opacity: 1, y: 0, scale: 1, filter: "blur(0px)" }}
                exit={{ opacity: 0, y: -24, scale: 0.985, filter: "blur(6px)" }}
                transition={panelSpring}
                className="absolute inset-0"
              >
                <StateCall />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>
    </div>
  );
}
