"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { motion } from "motion/react";
import { useAppKit, useAppKitAccount } from "@reown/appkit/react";
import {
  AnalyticsUpIcon,
  ArrowUpRight01Icon,
  CheckmarkCircle02Icon,
  Group01Icon,
  LockKeyIcon,
  ShieldBlockchainIcon,
  Wallet01Icon,
} from "hugeicons-react";

import { BorderBeam } from "@/components/ui/border-beam";
import { Button } from "@/components/ui/button";
import { NumberTicker } from "@/components/ui/number-ticker";
import type { ApiPick, DailyShortlist, TrackRecord } from "@/lib/meridian";
import { LINKS } from "@/lib/links";

const spring = { type: "spring" as const, stiffness: 400, damping: 30 };

/* ── Formatting helpers ──────────────────────────────────────────── */

function fmtUsd(n: number | null | undefined): string {
  if (n == null) return "—";
  if (n >= 1_000_000) return `$${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `$${(n / 1_000).toFixed(n >= 100_000 ? 0 : 1)}k`;
  return `$${n.toFixed(0)}`;
}

function fmtAge(hours: number | null | undefined): string {
  if (hours == null) return "—";
  if (hours < 1) return `${Math.round(hours * 60)}m`;
  if (hours < 24) return `${Math.round(hours)}h`;
  const d = Math.floor(hours / 24);
  const h = Math.round(hours % 24);
  return h ? `${d}d ${h}h` : `${d}d`;
}

function fmtPct(n: number | null | undefined): string {
  if (n == null) return "flat";
  const s = n >= 0 ? "+" : "−";
  return `${s}${Math.abs(n).toFixed(n >= 100 || n <= -100 ? 0 : 1)}%`;
}

function ticker(symbol: string): string {
  const s = symbol?.trim() ?? "";
  return s.startsWith("$") ? s : `$${s}`;
}

function scoreColor(score: number) {
  if (score >= 85) return "text-emerald-300";
  if (score >= 75) return "text-violet-300";
  if (score >= 60) return "text-sky-300";
  return "text-amber-300";
}

function authorityFlag(value: string | null | undefined): { text: string; tone: string } {
  if (!value || value === "Unknown") return { text: "unknown", tone: "text-zinc-500" };
  if (value === "renounced") return { text: "renounced ✓", tone: "text-emerald-300" };
  return { text: "live ⚠", tone: "text-amber-300" };
}

/* ── Scout chips (3 live scouts + smart-money as v1.5) ───────────── */

type ScoutVisual = "strong" | "ok" | "weak" | "unknown" | "soon";

const SCOUT_META = [
  { key: "onchain", label: "On-chain", icon: ShieldBlockchainIcon },
  { key: "liquidity", label: "Liquidity", icon: Wallet01Icon },
  { key: "momentum", label: "Momentum", icon: AnalyticsUpIcon },
  { key: "smart_money", label: "Smart-money", icon: Group01Icon },
] as const;

const SCOUT_PALETTE: Record<ScoutVisual, { dot: string; text: string }> = {
  strong: { dot: "bg-emerald-400", text: "text-emerald-300" },
  ok: { dot: "bg-violet-400", text: "text-violet-300" },
  weak: { dot: "bg-amber-400", text: "text-amber-300" },
  unknown: { dot: "bg-zinc-500", text: "text-zinc-400" },
  soon: { dot: "bg-zinc-600", text: "text-zinc-500" },
};

function scoutVisual(key: string, score: number | null): ScoutVisual {
  if (key === "smart_money") return "soon"; // honest: not shipped in v1
  if (score == null) return "unknown";
  if (score >= 75) return "strong";
  if (score >= 55) return "ok";
  return "weak";
}

function ScoutChip({
  label,
  visual,
  icon: Icon,
}: {
  label: string;
  visual: ScoutVisual;
  icon: typeof ShieldBlockchainIcon;
}) {
  const p = SCOUT_PALETTE[visual];
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full border border-white/10 bg-white/[0.03] px-2.5 py-1">
      <Icon className={`size-3 ${p.text}`} strokeWidth={1.8} />
      <span className="font-mono text-[10px] uppercase tracking-[0.12em] text-zinc-400">
        {label}
      </span>
      {visual === "soon" ? (
        <span className="font-mono text-[9px] uppercase tracking-[0.1em] text-zinc-600">v1.5</span>
      ) : (
        <span className={`size-1.5 rounded-full ${p.dot}`} />
      )}
    </span>
  );
}

/* ── Pick card ───────────────────────────────────────────────────── */

function MetricCell({ label, value, tone }: { label: string; value: string; tone?: string }) {
  return (
    <div>
      <div className={`font-mono text-xs ${tone ?? "text-zinc-300"}`}>{value}</div>
      <div className="font-mono text-[9px] uppercase tracking-[0.14em] text-zinc-600">{label}</div>
    </div>
  );
}

function PickCard({ pick, index }: { pick: ApiPick; index: number }) {
  const m = pick.metrics ?? {};
  const mint = authorityFlag(m.mint_authority);
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-10%" }}
      transition={{ ...spring, delay: index * 0.08 }}
      className="relative overflow-hidden rounded-2xl border border-white/10 bg-[#080A14] p-5 sm:p-6"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="flex size-9 shrink-0 items-center justify-center rounded-xl border border-violet-500/30 bg-violet-500/10 font-mono text-sm font-semibold text-violet-300">
            {pick.rank}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-heading text-lg font-semibold tracking-tight text-foreground">
                {ticker(pick.token.symbol)}
              </span>
              <span className="font-mono text-[11px] text-muted-foreground">{pick.token.name}</span>
            </div>
            <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-emerald-300">
              Surfaced today
            </span>
          </div>
        </div>
        <div className="text-right">
          <div className={`font-heading text-3xl font-semibold tracking-tight ${scoreColor(pick.composite_score)}`}>
            {pick.composite_score}
          </div>
          <div className="font-mono text-[9px] uppercase tracking-[0.18em] text-zinc-600">/ 100</div>
        </div>
      </div>

      {/* Scout breakdown */}
      <div className="mt-4 flex flex-wrap gap-1.5">
        {SCOUT_META.map((s) => (
          <ScoutChip
            key={s.key}
            label={s.label}
            visual={scoutVisual(s.key, pick.scores[s.key as keyof typeof pick.scores])}
            icon={s.icon}
          />
        ))}
      </div>

      {/* Metrics strip */}
      <div className="mt-5 grid grid-cols-2 gap-x-4 gap-y-3 rounded-xl border border-white/5 bg-white/[0.015] p-4 sm:grid-cols-4">
        <MetricCell label="Liquidity" value={fmtUsd(m.liquidity_usd)} />
        <MetricCell label="Pair age" value={fmtAge(m.age_hours)} />
        <MetricCell
          label="Buy/sell 1h"
          value={m.buy_sell_ratio_h1 != null ? `${m.buy_sell_ratio_h1.toFixed(1)}x` : "—"}
        />
        <MetricCell label="Mint auth" value={mint.text} tone={mint.tone} />
      </div>

      {/* Why it surfaced */}
      <div className="mt-5 space-y-2">
        {pick.top_reasons.map((reason) => (
          <div key={reason} className="flex items-start gap-2">
            <CheckmarkCircle02Icon className="mt-0.5 size-4 shrink-0 text-violet-400" strokeWidth={1.8} />
            <span className="text-sm leading-relaxed text-zinc-300">{reason}</span>
          </div>
        ))}
      </div>

      {/* Risk + read */}
      <div className="mt-5 grid gap-3 border-t border-white/5 pt-4 sm:grid-cols-[auto_1fr] sm:gap-x-6">
        <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-amber-300">
          Standout risk
        </span>
        <span className="text-sm text-zinc-400">{pick.standout_risk}</span>
      </div>
      <p className="mt-3 text-sm leading-relaxed text-zinc-300">
        <span className="text-zinc-500">Read — </span>
        {pick.one_line_read}
      </p>

      <div className="mt-4 flex items-center justify-between gap-3">
        <span className="inline-flex items-center gap-1.5 rounded-full border border-violet-500/25 bg-violet-500/[0.06] px-3 py-1 font-mono text-[10px] uppercase tracking-[0.18em] text-violet-300">
          Worth investigating
        </span>
        {pick.token.pair_url ? (
          <a
            href={pick.token.pair_url}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1 font-mono text-[11px] text-zinc-400 transition-colors hover:text-violet-300"
          >
            View pair
            <ArrowUpRight01Icon className="size-3.5" strokeWidth={2} />
          </a>
        ) : null}
      </div>
    </motion.div>
  );
}

function LockedPick({ pick, index }: { pick: ApiPick; index: number }) {
  return (
    <div className="relative overflow-hidden rounded-2xl">
      <div className="pointer-events-none select-none blur-[6px]" aria-hidden>
        <PickCard pick={pick} index={index} />
      </div>
      <div className="absolute inset-0 flex items-center justify-center bg-[#070912]/40">
        <div className="flex items-center gap-2 rounded-full border border-violet-500/25 bg-[#0B0D18]/90 px-4 py-2">
          <LockKeyIcon className="size-4 text-violet-300" strokeWidth={2} />
          <span className="font-mono text-[11px] uppercase tracking-[0.16em] text-violet-200">
            Hold $MRDN to unlock #{pick.rank}
          </span>
        </div>
      </div>
    </div>
  );
}

/* ── Empty state (backend offline or no run yet) ─────────────────── */

function AwaitingScan() {
  return (
    <div className="rounded-2xl border border-white/10 bg-[#080A14] p-10 text-center">
      <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-violet-300">
        Awaiting today&apos;s scan
      </p>
      <p className="mx-auto mt-3 max-w-md text-sm leading-relaxed text-zinc-400">
        The swarm hasn&apos;t published a shortlist yet. Once today&apos;s scan completes, the ranked
        picks appear here — and every one is logged to the public track record below.
      </p>
    </div>
  );
}

/* ── Track record ────────────────────────────────────────────────── */

const STATUS_VIEW = {
  hit: { glyph: "▲", text: "text-emerald-300", label: "played out" },
  miss: { glyph: "▼", text: "text-red-300", label: "faded" },
  open: { glyph: "•", text: "text-violet-300", label: "watching" },
} as const;

function TrackRecordSection({ data }: { data: TrackRecord | null }) {
  const summary = data?.summary;
  const calls = data?.calls ?? [];
  const hasCalls = (summary?.total_calls ?? 0) > 0;

  return (
    <div className="mt-16">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-violet-400">
            [ Track Record ]
          </p>
          <h2 className="font-heading mt-3 text-2xl font-semibold tracking-tight text-foreground md:text-3xl">
            Every call, kept honest.
          </h2>
        </div>
        <div className="flex gap-6">
          <div>
            <div className="font-heading text-2xl font-semibold tracking-tight text-foreground">
              <NumberTicker value={summary?.total_calls ?? 0} />
            </div>
            <div className="font-mono text-[9px] uppercase tracking-[0.18em] text-muted-foreground">
              Calls logged
            </div>
          </div>
          <div>
            <div className="font-heading text-2xl font-semibold tracking-tight text-foreground">
              {summary?.hit_rate != null ? `${Math.round(summary.hit_rate * 100)}%` : "—"}
            </div>
            <div className="font-mono text-[9px] uppercase tracking-[0.18em] text-muted-foreground">
              Hit rate
            </div>
          </div>
          <div>
            <div className="font-heading text-2xl font-semibold tracking-tight text-foreground">
              {summary?.open ?? 0}
            </div>
            <div className="font-mono text-[9px] uppercase tracking-[0.18em] text-muted-foreground">
              Open calls
            </div>
          </div>
        </div>
      </div>

      {hasCalls ? (
        <div className="mt-6 overflow-hidden rounded-2xl border border-white/10 bg-[#080A14]">
          {calls.map((row, i) => {
            const v = STATUS_VIEW[row.status] ?? STATUS_VIEW.open;
            return (
              <motion.div
                key={`${row.date}-${row.token.symbol}-${i}`}
                initial={{ opacity: 0, x: -10 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true, margin: "-5%" }}
                transition={{ ...spring, delay: i * 0.05 }}
                className="grid grid-cols-[auto_1fr_auto] items-center gap-4 border-b border-white/5 px-5 py-3.5 last:border-b-0 sm:grid-cols-[5rem_1fr_auto_auto]"
              >
                <span className="font-mono text-[11px] uppercase tracking-[0.12em] text-zinc-600">
                  {row.date}
                </span>
                <span className="font-mono text-sm text-zinc-200">{ticker(row.token.symbol)}</span>
                <span className="hidden font-mono text-xs text-zinc-500 sm:inline">
                  scored {row.score_at_call}
                </span>
                <span className={`flex items-center justify-end gap-2 font-mono text-xs ${v.text}`}>
                  <span>{v.glyph}</span>
                  <span className="uppercase tracking-[0.12em]">{v.label}</span>
                  <span className="w-14 text-right text-zinc-400">{fmtPct(row.pct_change)}</span>
                </span>
              </motion.div>
            );
          })}
        </div>
      ) : (
        <div className="mt-6 rounded-2xl border border-white/10 bg-[#080A14] p-8 text-center">
          <p className="text-sm leading-relaxed text-zinc-400">
            The record starts with today&apos;s picks. Outcomes update as calls play out —
            <span className="text-zinc-300"> wins and misses both shown</span>, never cherry-picked.
          </p>
        </div>
      )}

      <p className="mt-4 text-center font-mono text-[11px] text-zinc-600">
        Wins and misses both shown. Not financial advice.
      </p>
    </div>
  );
}

/* ── Main ─────────────────────────────────────────────────────────── */

export function MeridianShortlist({
  shortlist,
  trackRecord,
}: {
  shortlist: DailyShortlist | null;
  trackRecord: TrackRecord | null;
}) {
  const picks = shortlist?.picks ?? [];
  const freeCutoff = shortlist?.free_tier_cutoff ?? 1;
  const asOf = shortlist?.as_of_date ?? "—";

  // Wallet-connect hold-to-unlock: connect via Reown, check $MRDN balance, and
  // reveal the locked picks for holders.
  const { open } = useAppKit();
  const { address, isConnected } = useAppKitAccount();
  const [holder, setHolder] = useState<{ holds: boolean; balance: number } | null>(null);
  const [checking, setChecking] = useState(false);

  useEffect(() => {
    if (!address) return;
    let cancelled = false;
    // eslint-disable-next-line react-hooks/set-state-in-effect -- loading flag for a fetch-on-change
    setChecking(true);
    fetch(`/api/holder?wallet=${address}`)
      .then((r) => r.json())
      .then((d) => {
        if (!cancelled) setHolder({ holds: !!d.holds, balance: d.balance ?? 0 });
      })
      .catch(() => {
        if (!cancelled) setHolder({ holds: false, balance: 0 });
      })
      .finally(() => {
        if (!cancelled) setChecking(false);
      });
    return () => {
      cancelled = true;
    };
  }, [address]);

  // Guard on `address` so locked picks re-lock immediately on disconnect.
  const unlocked = !!address && holder?.holds === true;

  return (
    <div className="relative z-10 mx-auto max-w-5xl px-5 sm:px-6 md:px-10">
      {/* Header */}
      <div className="mb-10 text-center">
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={spring}
          className="font-mono text-[10px] uppercase tracking-[0.22em] text-violet-400"
        >
          [ Today&apos;s Shortlist ]
        </motion.p>
        <motion.h1
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ ...spring, delay: 0.08 }}
          className="font-heading mx-auto mt-4 max-w-3xl text-4xl font-semibold leading-[0.95] tracking-tight text-foreground md:text-5xl lg:text-6xl"
        >
          Today&apos;s shortlist.
          <br />
          <span className="bg-gradient-to-r from-sky-300 via-violet-400 to-violet-600 bg-clip-text text-transparent">
            Worth investigating.
          </span>
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ ...spring, delay: 0.14 }}
          className="mx-auto mt-5 max-w-xl text-sm leading-relaxed text-muted-foreground md:text-base"
        >
          The swarm scanned today&apos;s Solana launches and ranked the few that cleared the rubric.
          Every pick is framed as worth investigating — never financial advice.
        </motion.p>
      </div>

      {/* Scan status bar */}
      <div className="rounded-2xl border border-white/10 bg-[#0F1320]/60 p-4 backdrop-blur-sm sm:p-5">
        <div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap sm:items-center sm:gap-x-5 sm:gap-y-2">
          {[
            { label: picks.length ? "Daily scan complete" : "Awaiting scan", ok: picks.length > 0 },
            { label: `${picks.length} surfaced`, ok: true },
            { label: `as of ${asOf}`, ok: true },
            { label: `source · ${shortlist?.data_source ?? "—"}`, ok: true },
          ].map((row) => (
            <div
              key={row.label}
              className="flex items-center gap-2 font-mono text-[10px] uppercase tracking-[0.18em] text-muted-foreground"
            >
              <span className="relative flex size-1.5 shrink-0">
                <span
                  className={`absolute inline-flex size-full rounded-full ${row.ok ? "animate-ping bg-emerald-400 opacity-60" : "bg-zinc-600"}`}
                />
                <span className={`relative inline-flex size-1.5 rounded-full ${row.ok ? "bg-emerald-400" : "bg-zinc-600"}`} />
              </span>
              <span>{row.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Terminal surface with the ranked picks */}
      <div className="relative mt-8">
        <div className="pointer-events-none absolute -inset-10 rounded-[40px] bg-[radial-gradient(60%_50%_at_50%_50%,rgba(139,92,246,0.18),transparent_75%)] blur-2xl" />

        <div className="relative overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-b from-[#10131F] via-[#0B0D18] to-[#070912] shadow-[0_1px_0_rgba(255,255,255,0.06)_inset,0_24px_48px_-24px_rgba(0,0,0,0.8),0_40px_80px_-32px_rgba(139,92,246,0.35)] ring-1 ring-white/5">
          <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent" />

          {/* Title bar */}
          <div className="relative flex h-10 items-center border-b border-white/5 bg-gradient-to-b from-[#161A2A] to-[#121524] px-4">
            <div className="flex items-center gap-2">
              <span className="size-3 rounded-full bg-[#ff5f57] ring-1 ring-black/20" />
              <span className="size-3 rounded-full bg-[#febc2e] ring-1 ring-black/20" />
              <span className="size-3 rounded-full bg-[#28c840] ring-1 ring-black/20" />
            </div>
            <div className="pointer-events-none absolute inset-x-0 flex justify-center">
              <span className="font-mono text-[11px] tracking-wide text-zinc-500">meridian-swarm</span>
            </div>
            <div className="ml-auto flex items-center gap-2">
              <span className="relative flex size-1.5">
                <span className="absolute inline-flex size-full animate-ping rounded-full bg-emerald-400 opacity-60" />
                <span className="relative inline-flex size-1.5 rounded-full bg-emerald-400" />
              </span>
              <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-zinc-500">ranked</span>
            </div>
          </div>

          {/* Picks */}
          <div className="space-y-4 p-5 sm:p-6 md:p-8">
            {picks.length === 0 ? (
              <AwaitingScan />
            ) : (
              picks.map((pick, i) =>
                i < freeCutoff || unlocked ? (
                  <PickCard key={pick.token.address || pick.rank} pick={pick} index={i} />
                ) : (
                  <LockedPick key={pick.token.address || pick.rank} pick={pick} index={i} />
                ),
              )
            )}

            {/* Holder gate — connect wallet → check $MRDN balance → unlock */}
            {picks.length > freeCutoff && (
              <div className="rounded-2xl border border-violet-500/25 bg-violet-500/[0.05] p-5">
                {unlocked ? (
                  <div className="flex items-center gap-3">
                    <CheckmarkCircle02Icon className="size-4 shrink-0 text-emerald-300" strokeWidth={2} />
                    <p className="text-sm leading-relaxed text-zinc-300">
                      <span className="text-emerald-300">Holder verified</span> — full shortlist
                      unlocked{holder ? ` (${holder.balance.toLocaleString()} $MRDN)` : ""}.
                    </p>
                  </div>
                ) : (
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                    <div className="flex items-start gap-3">
                      <LockKeyIcon className="mt-0.5 size-4 shrink-0 text-violet-300" strokeWidth={2} />
                      <p className="text-sm leading-relaxed text-zinc-300">
                        {isConnected ? (
                          <>
                            This wallet holds{" "}
                            <span className="text-amber-300">0 $MRDN</span>. Hold $MRDN to unlock the
                            full ranked shortlist.
                          </>
                        ) : (
                          <>
                            The free tier shows the top {freeCutoff} pick
                            {freeCutoff === 1 ? "" : "s"}.{" "}
                            <span className="text-violet-300">Hold $MRDN</span> to unlock the full
                            shortlist + live track record.
                          </>
                        )}
                      </p>
                    </div>
                    <div className="flex shrink-0 items-center gap-2">
                      {checking ? (
                        <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-violet-300">
                          Checking…
                        </span>
                      ) : isConnected ? (
                        <a href={LINKS.marketplace} target="_blank" rel="noreferrer">
                          <Button variant="violet" size="pill">
                            Buy $MRDN
                            <ArrowUpRight01Icon className="size-4" strokeWidth={2.2} />
                          </Button>
                        </a>
                      ) : (
                        <Button variant="violet" size="pill" onClick={() => open()}>
                          <Wallet01Icon className="size-4" strokeWidth={2.2} />
                          Connect wallet
                        </Button>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          <BorderBeam size={140} duration={8} colorFrom="#A78BFA" colorTo="#1E2B4A" borderWidth={1.2} />
        </div>
      </div>

      {/* Track record */}
      <TrackRecordSection data={trackRecord} />

      {/* Back to site CTA */}
      <div className="mt-14 flex justify-center">
        <motion.div whileHover={{ scale: 0.97 }} whileTap={{ scale: 0.94 }}>
          <Link href="/#protocol">
            <Button variant="outline" size="pill">
              See how the track record works
              <ArrowUpRight01Icon className="size-4" strokeWidth={2.2} />
            </Button>
          </Link>
        </motion.div>
      </div>
    </div>
  );
}
