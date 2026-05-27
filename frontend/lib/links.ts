/**
 * Single source of truth for external links + on-chain $MRDN details.
 *
 * TODO when known:
 *  - LINKS.marketplace → the exact swarms.world $MRDN listing URL
 *  - SITE_URL (in app/layout.tsx) → the production Vercel domain
 */

export const TOKEN = {
  ticker: "MRDN",
  mint: "G7L2LRZyoE6FZgFo51Betj88UPMdnNi1iYmBrpfpswrm",
  pool: "Ha8Gs6P4BZAu3iu6ZAZj2PoA9xkA1Lf5mum5FjsdtnHh",
  supply: "1,000,000,000",
} as const;

export const LINKS = {
  github: "https://github.com/Enoch208/Meridian",
  // Swarms marketplace — swap for the exact $MRDN listing URL once you have it.
  marketplace: "https://swarms.world",
  solscan: `https://solscan.io/token/${TOKEN.mint}`,
  dexscreener: `https://dexscreener.com/solana/${TOKEN.pool}`,
  telegramBot: "https://t.me/usemeridianbot",
  swarmsX: "https://x.com/swarms_corp",
  swarmsDiscord: "https://discord.gg/VK9jp9sXwJ",
} as const;
