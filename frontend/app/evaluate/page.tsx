import type { Metadata } from "next";

import { SiteNavbar } from "@/components/layout/site-navbar";
import { SiteFooter } from "@/components/layout/site-footer";
import { EvaluatePanel } from "@/components/blocks/evaluate-panel";
import { AmbientGlow } from "@/components/ui/ambient-glow";

export const metadata: Metadata = {
  title: "Evaluate a token",
  description:
    "Paste any Solana token and have Meridian's scout swarm score it on the spot — composite score, scout breakdown, the standout risk, and a one-line read.",
};

export default function EvaluatePage() {
  return (
    <main className="flex min-h-screen flex-col bg-background text-foreground">
      <SiteNavbar />
      <section className="relative flex-1 overflow-clip pt-[calc(4rem+2rem)] pb-24 md:pt-[calc(4rem+3rem)]">
        <AmbientGlow position="top" intensity="medium" size={1000} />
        <AmbientGlow position="bottom-left" intensity="subtle" size={700} />
        <EvaluatePanel />
      </section>
      <SiteFooter />
    </main>
  );
}
