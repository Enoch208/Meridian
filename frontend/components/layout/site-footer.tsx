import Image from "next/image";
import Link from "next/link";
import { Github01Icon, NewTwitterIcon } from "hugeicons-react";

import { MeridianMark } from "@/components/ui/meridian-mark";
import { MeridianWordmark } from "@/components/ui/meridian-wordmark";
import { LINKS } from "@/lib/links";

type FooterLink = { label: string; href: string; external?: boolean };

const LINK_COLUMNS: { title: string; links: FooterLink[] }[] = [
  {
    title: "Product",
    links: [
      { label: "The Swarm", href: "/#use-cases" },
      { label: "How It Works", href: "/#lifecycle" },
      { label: "Track Record", href: "/#protocol" },
      { label: "See Today's Picks", href: "/demo" },
    ],
  },
  {
    title: "Token",
    links: [
      { label: "Trade on Swarms", href: LINKS.marketplace, external: true },
      { label: "$MRDN on Solscan", href: LINKS.solscan, external: true },
      { label: "Chart (DexScreener)", href: LINKS.dexscreener, external: true },
    ],
  },
  {
    title: "Resources",
    links: [
      { label: "Documentation", href: LINKS.github, external: true },
      { label: "The Thesis", href: LINKS.github, external: true },
      { label: "GitHub", href: LINKS.github, external: true },
    ],
  },
  {
    title: "Community",
    links: [
      { label: "Telegram bot", href: LINKS.telegramBot, external: true },
      { label: "Swarms on X", href: LINKS.swarmsX, external: true },
      { label: "Swarms Discord", href: LINKS.swarmsDiscord, external: true },
    ],
  },
];

export function SiteFooter() {
  return (
    <footer className="relative border-t border-white/5 bg-[#05060F]">
      <div className="mx-auto max-w-7xl px-6 py-24 md:px-10">
        <div className="grid gap-12 md:grid-cols-12">
          <div className="md:col-span-4">
            <div className="flex items-center gap-3">
              <MeridianMark size={36} />
              <MeridianWordmark height={22} />
            </div>
            <p className="mt-5 max-w-xs text-sm leading-relaxed text-muted-foreground">
              A swarm of scout agents that finds the few Solana launches worth
              investigating today — scored on a transparent rubric, with a
              public track record of every call.
            </p>
            <div className="mt-6 flex flex-wrap items-center gap-3">
              <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1.5">
                <Image
                  src="/brand/solana-mark.svg"
                  alt="Solana"
                  width={14}
                  height={14}
                  className="size-3.5"
                />
                <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-muted-foreground">
                  Built on Solana
                </span>
              </div>
              <div className="inline-flex items-center gap-2 rounded-full border border-violet-500/30 bg-violet-500/10 px-3 py-1.5">
                <span className="size-1.5 animate-pulse rounded-full bg-violet-400" />
                <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-violet-300">
                  Agent Capital Markets
                </span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-10 md:col-span-8 md:grid-cols-4">
            {LINK_COLUMNS.map((col) => (
              <div key={col.title}>
                <h3 className="font-mono text-[10px] uppercase tracking-[0.22em] text-muted-foreground">
                  {col.title}
                </h3>
                <ul className="mt-4 space-y-3">
                  {col.links.map((link) => (
                    <li key={link.label}>
                      <Link
                        href={link.href}
                        target={link.external ? "_blank" : undefined}
                        rel={link.external ? "noreferrer" : undefined}
                        className="text-sm text-zinc-300 transition-colors hover:text-violet-300"
                      >
                        {link.label}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-16 flex flex-col gap-6 border-t border-white/5 pt-8 md:flex-row md:items-center md:justify-between">
          <p className="font-mono text-[11px] text-muted-foreground">
            © 2026 Meridian. Worth investigating — never financial advice.
          </p>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              {[
                { icon: NewTwitterIcon, href: LINKS.swarmsX, label: "X" },
                { icon: Github01Icon, href: LINKS.github, label: "GitHub" },
              ].map(({ icon: Icon, href, label }) => (
                <a
                  key={label}
                  href={href}
                  target="_blank"
                  rel="noreferrer"
                  aria-label={label}
                  className="flex size-8 items-center justify-center rounded-full border border-white/10 bg-white/5 text-zinc-500 transition-colors hover:border-violet-500/30 hover:bg-violet-500/10 hover:text-violet-300"
                >
                  <Icon className="size-3.5" strokeWidth={1.5} />
                </a>
              ))}
            </div>
            <div className="hidden h-4 w-px bg-white/10 md:block" />
            <a
              href={LINKS.solscan}
              target="_blank"
              rel="noreferrer"
              className="rounded-md border border-white/10 bg-white/5 px-2.5 py-1 font-mono text-[11px] text-violet-300 transition-colors hover:border-violet-500/30 hover:text-violet-200"
            >
              $MRDN · G7L2…swrm
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
