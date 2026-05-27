"use client";

import { useState } from "react";
import { motion } from "motion/react";
import {
  ArrowUpRight01Icon,
  CheckmarkCircle02Icon,
  Copy01Icon,
} from "hugeicons-react";

import { AmbientGlow } from "@/components/ui/ambient-glow";
import { BorderBeam } from "@/components/ui/border-beam";
import { Button } from "@/components/ui/button";
import { LINKS, TOKEN } from "@/lib/links";

export function TokenBand() {
  const [copied, setCopied] = useState(false);

  function copyCA() {
    navigator.clipboard.writeText(TOKEN.mint);
    setCopied(true);
    setTimeout(() => setCopied(false), 1800);
  }

  const stats = [
    { label: "Ticker", value: `$${TOKEN.ticker}` },
    { label: "Supply", value: TOKEN.supply },
    { label: "Chain", value: "Solana" },
  ];

  return (
    <section id="token" className="relative overflow-hidden py-24 md:py-32">
      <AmbientGlow position="center" intensity="subtle" size={900} />

      <div className="relative z-10 mx-auto max-w-5xl px-6 md:px-10">
        <motion.div
          initial={{ opacity: 0, y: 32 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-15%" }}
          transition={{ type: "spring", stiffness: 300, damping: 35 }}
          className="relative overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-[#0F1320] via-[#0B0E18] to-[#070912] p-8 md:p-14"
        >
          <AmbientGlow position="center" intensity="medium" size={800} />
          <BorderBeam size={180} duration={9} colorFrom="#A78BFA" colorTo="#1E2B4A" />

          <div className="relative z-10">
            <div className="flex flex-col items-center text-center">
              <span className="inline-flex items-center gap-2 rounded-full border border-violet-500/30 bg-violet-500/10 px-4 py-1.5">
                <span className="relative flex size-1.5">
                  <span className="absolute inline-flex size-full animate-ping rounded-full bg-emerald-400 opacity-60" />
                  <span className="relative inline-flex size-1.5 rounded-full bg-emerald-400" />
                </span>
                <span className="font-mono text-[10px] uppercase tracking-[0.22em] text-violet-300">
                  Live on Solana
                </span>
              </span>

              <h2 className="font-heading mt-6 max-w-2xl text-4xl font-semibold leading-[0.98] tracking-tight text-foreground md:text-5xl lg:text-6xl">
                Hold{" "}
                <span className="bg-gradient-to-r from-sky-300 via-violet-400 to-violet-600 bg-clip-text text-transparent">
                  $MRDN
                </span>
                . Unlock the full feed.
              </h2>

              <p className="mt-5 max-w-xl text-base leading-relaxed text-muted-foreground">
                The free tier proves the product works. Holding $MRDN unlocks the
                full ranked shortlist in real time, plus the live track record —
                the daily loop is the reason to hold.
              </p>
            </div>

            {/* Contract address — copyable */}
            <div className="mx-auto mt-8 flex max-w-xl flex-col items-stretch gap-2 sm:flex-row sm:items-center">
              <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-zinc-500 sm:sr-only">
                Contract
              </span>
              <div className="flex flex-1 items-center gap-2 rounded-xl border border-white/10 bg-[#080A14] px-3 py-2.5">
                <code className="flex-1 truncate font-mono text-xs text-zinc-300">
                  {TOKEN.mint}
                </code>
                <button
                  type="button"
                  onClick={copyCA}
                  aria-label="Copy contract address"
                  className="flex shrink-0 cursor-pointer items-center gap-1 rounded-lg border border-white/10 bg-white/5 px-2.5 py-1.5 font-mono text-[10px] uppercase tracking-[0.18em] text-zinc-300 transition-colors hover:border-violet-500/30 hover:text-violet-300"
                >
                  {copied ? (
                    <>
                      <CheckmarkCircle02Icon className="size-3" strokeWidth={2.2} />
                      Copied
                    </>
                  ) : (
                    <>
                      <Copy01Icon className="size-3" strokeWidth={2.2} />
                      Copy
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Stats */}
            <div className="mx-auto mt-8 grid max-w-xl grid-cols-3 gap-px overflow-hidden rounded-xl border border-white/10 bg-white/[0.04]">
              {stats.map((s) => (
                <div key={s.label} className="bg-[#0B0E18] px-4 py-4 text-center">
                  <div className="font-heading text-lg font-semibold tracking-tight text-foreground md:text-xl">
                    {s.value}
                  </div>
                  <div className="mt-1 font-mono text-[9px] uppercase tracking-[0.18em] text-muted-foreground">
                    {s.label}
                  </div>
                </div>
              ))}
            </div>

            {/* CTAs */}
            <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
              <motion.div whileHover={{ scale: 0.97 }} whileTap={{ scale: 0.94 }}>
                <a href={LINKS.marketplace} target="_blank" rel="noreferrer">
                  <Button variant="violet" size="pill">
                    Trade $MRDN on Swarms
                    <ArrowUpRight01Icon className="size-4" strokeWidth={2.2} />
                  </Button>
                </a>
              </motion.div>
              <motion.div whileHover={{ scale: 0.97 }} whileTap={{ scale: 0.94 }}>
                <a href={LINKS.solscan} target="_blank" rel="noreferrer">
                  <Button variant="outline" size="pill">
                    View on Solscan
                  </Button>
                </a>
              </motion.div>
              <motion.div whileHover={{ scale: 0.97 }} whileTap={{ scale: 0.94 }}>
                <a href={LINKS.dexscreener} target="_blank" rel="noreferrer">
                  <Button variant="outline" size="pill">
                    Chart
                  </Button>
                </a>
              </motion.div>
            </div>

            <p className="mt-6 text-center font-mono text-[11px] text-zinc-600">
              Worth investigating — never financial advice.
            </p>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
