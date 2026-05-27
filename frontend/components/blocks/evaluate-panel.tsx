"use client";

import { useState } from "react";
import { motion } from "motion/react";
import {
  AnalyticsUpIcon,
  CheckmarkCircle02Icon,
  FlashIcon,
  Loading03Icon,
  ShieldBlockchainIcon,
} from "hugeicons-react";

import { Button } from "@/components/ui/button";
import { MERIDIAN_API_URL, type ApiPick } from "@/lib/meridian";

type Result =
  | { state: "idle" }
  | { state: "loading" }
  | { state: "error"; message: string }
  | { state: "done"; pick: ApiPick };

function scoreColor(score: number) {
  if (score >= 85) return "text-emerald-300";
  if (score >= 75) return "text-violet-300";
  if (score >= 60) return "text-sky-300";
  return "text-amber-300";
}

function fmtScore(v: number | null | undefined) {
  return v == null ? "—" : String(v);
}

const SCOUT_LABELS: [keyof ApiPick["scores"], string][] = [
  ["onchain", "On-chain"],
  ["liquidity", "Liquidity"],
  ["momentum", "Momentum"],
  ["smart_money", "Smart-money"],
];

export function EvaluatePanel() {
  const [token, setToken] = useState("");
  const [result, setResult] = useState<Result>({ state: "idle" });

  async function run() {
    const t = token.trim();
    if (!t) return;
    setResult({ state: "loading" });
    try {
      const ctrl = new AbortController();
      const timer = setTimeout(() => ctrl.abort(), 70_000); // tolerate a cold backend
      const res = await fetch(`${MERIDIAN_API_URL}/api/evaluate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token: t }),
        signal: ctrl.signal,
      });
      clearTimeout(timer);
      const data = await res.json();
      if (!data.found || !data.pick) {
        setResult({
          state: "error",
          message: data.error ?? "No Solana pair found for that token.",
        });
        return;
      }
      setResult({ state: "done", pick: data.pick as ApiPick });
    } catch {
      setResult({
        state: "error",
        message: "Couldn't reach the swarm — it may be waking up. Try again.",
      });
    }
  }

  return (
    <div className="relative z-10 mx-auto max-w-3xl px-5 sm:px-6 md:px-10">
      <div className="mb-8 text-center">
        <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-violet-400">
          [ Evaluate ]
        </p>
        <h1 className="font-heading mx-auto mt-4 max-w-2xl text-4xl font-semibold leading-[0.98] tracking-tight text-foreground md:text-5xl">
          Score any Solana token.
        </h1>
        <p className="mx-auto mt-4 max-w-lg text-sm leading-relaxed text-muted-foreground md:text-base">
          Paste a token address. The same scouts that build the daily shortlist
          grade it on the spot — worth investigating, never financial advice.
        </p>
      </div>

      {/* Input */}
      <div className="flex flex-col gap-2 sm:flex-row">
        <input
          value={token}
          onChange={(e) => setToken(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && run()}
          placeholder="Solana token / mint address"
          spellCheck={false}
          className="flex-1 rounded-xl border border-white/10 bg-[#0A0C14] px-4 py-3 font-mono text-sm text-zinc-100 placeholder:text-zinc-600 focus:border-violet-500/40 focus:outline-none focus:ring-2 focus:ring-violet-500/20"
        />
        <motion.div whileHover={{ scale: 0.98 }} whileTap={{ scale: 0.95 }}>
          <Button
            variant="violet"
            size="pill"
            onClick={run}
            disabled={!token.trim() || result.state === "loading"}
            className="w-full sm:w-auto"
          >
            {result.state === "loading" ? (
              <>
                <Loading03Icon className="size-4 animate-spin" strokeWidth={2.2} />
                Scanning
              </>
            ) : (
              <>
                <FlashIcon className="size-4" strokeWidth={2.2} />
                Evaluate
              </>
            )}
          </Button>
        </motion.div>
      </div>

      {/* Result */}
      <div className="mt-8">
        {result.state === "loading" && (
          <div className="rounded-2xl border border-white/10 bg-[#0A0C14] p-8 text-center font-mono text-xs uppercase tracking-[0.18em] text-violet-300">
            Scoring against the rubric…
          </div>
        )}

        {result.state === "error" && (
          <div className="rounded-2xl border border-amber-500/25 bg-amber-500/[0.05] p-5 text-sm text-amber-200">
            {result.message}
          </div>
        )}

        {result.state === "done" && <ResultCard pick={result.pick} />}
      </div>
    </div>
  );
}

function ResultCard({ pick }: { pick: ApiPick }) {
  const sym = pick.token.symbol?.startsWith("$")
    ? pick.token.symbol
    : `$${pick.token.symbol}`;

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: "spring", stiffness: 320, damping: 32 }}
      className="relative overflow-hidden rounded-2xl border border-white/10 bg-[#0A0C14] p-6"
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-heading text-xl font-semibold tracking-tight text-foreground">
              {sym}
            </span>
            <span className="font-mono text-[11px] text-muted-foreground">
              {pick.token.name}
            </span>
          </div>
          {pick.token.pair_url && (
            <a
              href={pick.token.pair_url}
              target="_blank"
              rel="noreferrer"
              className="font-mono text-[10px] uppercase tracking-[0.18em] text-violet-300 hover:text-violet-200"
            >
              View pair ↗
            </a>
          )}
        </div>
        <div className="text-right">
          <div className={`font-heading text-4xl font-semibold tracking-tight ${scoreColor(pick.composite_score)}`}>
            {pick.composite_score}
          </div>
          <div className="font-mono text-[9px] uppercase tracking-[0.18em] text-zinc-600">
            / 100
          </div>
        </div>
      </div>

      {/* Scout breakdown */}
      <div className="mt-5 grid grid-cols-2 gap-2 sm:grid-cols-4">
        {SCOUT_LABELS.map(([key, label]) => {
          const v = pick.scores[key];
          const unknown = v == null;
          return (
            <div
              key={key}
              className="rounded-xl border border-white/10 bg-white/[0.03] px-3 py-2.5 text-center"
            >
              <div className={`font-heading text-lg font-semibold ${unknown ? "text-zinc-500" : scoreColor(v as number)}`}>
                {fmtScore(v)}
              </div>
              <div className="mt-0.5 font-mono text-[9px] uppercase tracking-[0.14em] text-muted-foreground">
                {label}
              </div>
            </div>
          );
        })}
      </div>

      {/* Reasons */}
      {pick.top_reasons.length > 0 && (
        <div className="mt-5 space-y-2">
          {pick.top_reasons.map((reason) => (
            <div key={reason} className="flex items-start gap-2">
              <CheckmarkCircle02Icon
                className="mt-0.5 size-4 shrink-0 text-violet-400"
                strokeWidth={1.8}
              />
              <span className="text-sm leading-relaxed text-zinc-300">{reason}</span>
            </div>
          ))}
        </div>
      )}

      {/* Risk + read */}
      <div className="mt-5 flex items-start gap-2 border-t border-white/5 pt-4">
        <ShieldBlockchainIcon className="mt-0.5 size-4 shrink-0 text-amber-300" strokeWidth={1.8} />
        <div>
          <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-amber-300">
            Standout risk
          </span>
          <p className="mt-1 text-sm text-zinc-400">{pick.standout_risk}</p>
        </div>
      </div>
      <p className="mt-3 flex items-start gap-2 text-sm leading-relaxed text-zinc-300">
        <AnalyticsUpIcon className="mt-0.5 size-4 shrink-0 text-violet-400" strokeWidth={1.8} />
        <span>{pick.one_line_read}</span>
      </p>

      <div className="mt-5 flex items-center justify-between border-t border-white/5 pt-4">
        <span className="inline-flex items-center rounded-full border border-violet-500/25 bg-violet-500/[0.06] px-3 py-1 font-mono text-[10px] uppercase tracking-[0.18em] text-violet-300">
          Worth investigating
        </span>
        <span className="font-mono text-[10px] text-zinc-600">Not financial advice</span>
      </div>
    </motion.div>
  );
}
