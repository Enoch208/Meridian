"use client";

import { useState } from "react";
import { motion } from "motion/react";
import {
  AnalyticsUpIcon,
  CheckmarkCircle02Icon,
  FlashIcon,
  Loading03Icon,
  NewTwitterIcon,
  ShieldBlockchainIcon,
  TelegramIcon,
} from "hugeicons-react";

import { Button } from "@/components/ui/button";
import { MERIDIAN_API_URL, type ApiPick, type TokenMetrics } from "@/lib/meridian";

type SecurityCheck = {
  overall_score?: number | null;
  is_honeypot?: boolean | null;
  buy_tax?: number | null;
  sell_tax?: number | null;
  liquidity_locked_pct?: number | null;
};

type Result =
  | { state: "idle" }
  | { state: "loading" }
  | { state: "error"; message: string }
  | { state: "done"; pick: ApiPick; security: SecurityCheck | null };

function scoreColor(score: number) {
  if (score >= 85) return "text-emerald-300";
  if (score >= 75) return "text-violet-300";
  if (score >= 60) return "text-sky-300";
  return "text-amber-300";
}

function fmtScore(v: number | null | undefined) {
  return v == null ? "—" : String(v);
}

function fmtUsd(n?: number | null): string {
  if (n == null) return "—";
  if (n >= 1e9) return `$${(n / 1e9).toFixed(1)}B`;
  if (n >= 1e6) return `$${(n / 1e6).toFixed(1)}M`;
  if (n >= 1e3) return `$${(n / 1e3).toFixed(n >= 1e5 ? 0 : 1)}k`;
  return `$${n.toFixed(0)}`;
}

function fmtPrice(n?: number | null): string {
  if (n == null) return "—";
  if (n >= 1) return `$${n.toFixed(2)}`;
  if (n >= 0.0001) return `$${n.toFixed(6)}`;
  return `$${n.toExponential(2)}`;
}

function fmtAge(h?: number | null): string {
  if (h == null) return "—";
  if (h < 1) return `${Math.round(h * 60)}m`;
  if (h < 24) return `${Math.round(h)}h`;
  return `${Math.floor(h / 24)}d`;
}

function authority(v?: string | null) {
  if (v === "renounced") return <span className="text-emerald-300">Renounced</span>;
  if (v && v.startsWith("live")) return <span className="text-amber-300">Live ⚠</span>;
  return <span className="text-zinc-500">Unknown</span>;
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
      setResult({
        state: "done",
        pick: data.pick as ApiPick,
        security: (data.security ?? null) as SecurityCheck | null,
      });
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

        {result.state === "done" && (
          <ResultCard pick={result.pick} security={result.security} />
        )}
      </div>
    </div>
  );
}

function ResultCard({ pick, security }: { pick: ApiPick; security: SecurityCheck | null }) {
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
        <div className="flex items-start gap-3">
          {pick.token.image_url && (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={pick.token.image_url}
              alt={pick.token.symbol}
              className="size-10 shrink-0 rounded-full border border-white/10 object-cover"
            />
          )}
          <div>
          <div className="flex items-center gap-2">
            <span className="font-heading text-xl font-semibold tracking-tight text-foreground">
              {sym}
            </span>
            <span className="font-mono text-[11px] text-muted-foreground">
              {pick.token.name}
            </span>
            {pick.metrics?.launchpad && (
              <span className="rounded-full border border-violet-500/25 bg-violet-500/[0.06] px-2 py-0.5 font-mono text-[9px] uppercase tracking-[0.12em] text-violet-300">
                {pick.metrics.launchpad}
              </span>
            )}
          </div>
          <div className="mt-1.5 flex flex-wrap items-center gap-3">
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
            {pick.token.twitter && (
              <a href={pick.token.twitter} target="_blank" rel="noreferrer" aria-label="X" className="text-zinc-500 hover:text-violet-300">
                <NewTwitterIcon className="size-3.5" strokeWidth={1.8} />
              </a>
            )}
            {pick.token.telegram && (
              <a href={pick.token.telegram} target="_blank" rel="noreferrer" aria-label="Telegram" className="text-zinc-500 hover:text-violet-300">
                <TelegramIcon className="size-3.5" strokeWidth={1.8} />
              </a>
            )}
            {pick.token.website && (
              <a href={pick.token.website} target="_blank" rel="noreferrer" className="font-mono text-[10px] uppercase tracking-[0.18em] text-zinc-500 hover:text-violet-300">
                Site ↗
              </a>
            )}
          </div>
          </div>
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

      {pick.metrics && <MetricsGrid m={pick.metrics} />}

      {security && <SecuritySection s={security} />}

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

function MetricsGrid({ m }: { m: TokenMetrics }) {
  const pct = m.price_change_24h;
  const tiles: { label: string; value: React.ReactNode }[] = [];
  if (m.price_usd != null) tiles.push({ label: "Price", value: fmtPrice(m.price_usd) });
  if (pct != null)
    tiles.push({
      label: "24h",
      value: (
        <span className={pct >= 0 ? "text-emerald-300" : "text-red-300"}>
          {(pct >= 0 ? "+" : "−") + Math.abs(pct).toFixed(Math.abs(pct) >= 100 ? 0 : 1)}%
        </span>
      ),
    });
  if (m.liquidity_usd != null) tiles.push({ label: "Liquidity", value: fmtUsd(m.liquidity_usd) });
  if (m.market_cap != null) tiles.push({ label: "Market cap", value: fmtUsd(m.market_cap) });
  else if (m.fdv != null) tiles.push({ label: "FDV", value: fmtUsd(m.fdv) });
  if (m.volume_h24 != null) tiles.push({ label: "24h Vol", value: fmtUsd(m.volume_h24) });
  if (m.age_hours != null) tiles.push({ label: "Age", value: fmtAge(m.age_hours) });
  if (m.holder_count != null)
    tiles.push({ label: "Holders", value: m.holder_count.toLocaleString() });
  if (m.buys_h1 != null || m.sells_h1 != null)
    tiles.push({
      label: "Buys / Sells 1h",
      value: `${m.buys_h1 ?? "—"} / ${m.sells_h1 ?? "—"}`,
    });
  tiles.push({ label: "Mint auth", value: authority(m.mint_authority) });
  tiles.push({ label: "Freeze auth", value: authority(m.freeze_authority) });

  return (
    <div className="mt-5 grid grid-cols-2 gap-2 sm:grid-cols-3">
      {tiles.map((t) => (
        <div
          key={t.label}
          className="rounded-lg border border-white/5 bg-[#0A0C14] px-3 py-2"
        >
          <div className="font-mono text-xs text-zinc-200">{t.value}</div>
          <div className="mt-0.5 font-mono text-[9px] uppercase tracking-[0.14em] text-muted-foreground">
            {t.label}
          </div>
        </div>
      ))}
    </div>
  );
}

function SecuritySection({ s }: { s: SecurityCheck }) {
  const hp = s.is_honeypot;
  const rows = [
    s.overall_score != null && { label: "Safety", value: `${s.overall_score}/100` },
    (s.buy_tax != null || s.sell_tax != null) && {
      label: "Buy / Sell tax",
      value: `${s.buy_tax ?? "—"}% / ${s.sell_tax ?? "—"}%`,
    },
    s.liquidity_locked_pct != null && {
      label: "Liquidity locked",
      value: `${s.liquidity_locked_pct}%`,
    },
  ].filter(Boolean) as { label: string; value: string }[];

  return (
    <div className="mt-5 rounded-xl border border-white/10 bg-white/[0.03] p-4">
      <div className="flex items-center justify-between">
        <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-zinc-500">
          Security check
        </span>
        {hp != null && (
          <span
            className={`font-mono text-[10px] uppercase tracking-[0.18em] ${hp ? "text-red-300" : "text-emerald-300"}`}
          >
            {hp ? "⛔ Honeypot" : "✓ Not a honeypot"}
          </span>
        )}
      </div>
      {rows.length > 0 && (
        <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-3">
          {rows.map((r) => (
            <div
              key={r.label}
              className="rounded-lg border border-white/5 bg-[#0A0C14] px-3 py-2"
            >
              <div className="font-mono text-xs text-zinc-200">{r.value}</div>
              <div className="mt-0.5 font-mono text-[9px] uppercase tracking-[0.14em] text-muted-foreground">
                {r.label}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
