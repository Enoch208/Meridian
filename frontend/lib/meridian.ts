/**
 * Meridian backend client — the typed contract between this frontend and the
 * Python scout-swarm API (see backend/README.md and spec §7).
 *
 * Fetches run server-side (uncached/dynamic by default in Next 16), so the
 * `/demo` page always renders the latest shortlist + track record.
 */

export const MERIDIAN_API_URL =
  process.env.NEXT_PUBLIC_MERIDIAN_API_URL ?? "http://localhost:8000";

/* ── Backend response types (mirror backend/meridian/api/schemas.py) ──────── */

export type TokenInfo = {
  name: string;
  symbol: string;
  address: string;
  pair_url?: string | null;
};

export type ScoreBreakdown = {
  onchain: number | null;
  liquidity: number | null;
  momentum: number | null;
  smart_money: number | null;
};

export type TokenMetrics = {
  liquidity_usd?: number | null;
  fdv?: number | null;
  market_cap?: number | null;
  age_hours?: number | null;
  volume_h24?: number | null;
  buy_sell_ratio_h1?: number | null;
  buys_h1?: number | null;
  sells_h1?: number | null;
  price_usd?: number | null;
  price_change_24h?: number | null;
  launchpad?: string | null;
  mint_authority?: string | null;
  freeze_authority?: string | null;
};

export type ApiPick = {
  rank: number;
  token: TokenInfo;
  composite_score: number;
  scores: ScoreBreakdown;
  top_reasons: string[];
  standout_risk: string;
  one_line_read: string;
  metrics?: TokenMetrics | null;
  unknowns: string[];
};

export type DailyShortlist = {
  generated_at: string | null;
  as_of_date: string | null;
  data_source: string;
  disclaimer: string;
  free_tier_cutoff: number;
  picks: ApiPick[];
};

export type CallStatus = "hit" | "miss" | "open";

export type CallRecord = {
  date: string;
  rank: number;
  token: TokenInfo;
  score_at_call: number;
  price_at_call_usd?: number | null;
  price_now_usd?: number | null;
  pct_change?: number | null;
  status: CallStatus;
};

export type TrackRecord = {
  updated_at: string;
  summary: {
    total_calls: number;
    hits: number;
    misses: number;
    open: number;
    hit_rate: number | null;
  };
  calls: CallRecord[];
};

/* ── Fetchers (return null on failure so the UI degrades gracefully) ──────── */

async function getJson<T>(path: string): Promise<T | null> {
  try {
    const res = await fetch(`${MERIDIAN_API_URL}${path}`, { cache: "no-store" });
    if (!res.ok) return null;
    return (await res.json()) as T;
  } catch {
    return null;
  }
}

export function getDailyShortlist(): Promise<DailyShortlist | null> {
  return getJson<DailyShortlist>("/api/daily-shortlist");
}

export function getTrackRecord(): Promise<TrackRecord | null> {
  return getJson<TrackRecord>("/api/track-record");
}
