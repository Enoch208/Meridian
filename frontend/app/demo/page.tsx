import type { Metadata } from "next";

import { SiteNavbar } from "@/components/layout/site-navbar";
import { SiteFooter } from "@/components/layout/site-footer";
import { MeridianShortlist } from "@/components/blocks/meridian-shortlist";
import { AmbientGlow } from "@/components/ui/ambient-glow";
import { getDailyShortlist, getTrackRecord } from "@/lib/meridian";

export const metadata: Metadata = {
  title: "Today's Shortlist",
  description:
    "See the Meridian scout swarm's daily ranked shortlist of Solana launches worth investigating — with composite scores, scout breakdowns, and a public track record of past calls.",
};

// Always render fresh from the live swarm backend.
export const dynamic = "force-dynamic";

export default async function DemoPage() {
  const [shortlist, trackRecord] = await Promise.all([
    getDailyShortlist(),
    getTrackRecord(),
  ]);

  return (
    <main className="flex min-h-screen flex-col bg-background text-foreground">
      <SiteNavbar />
      <section className="relative flex-1 overflow-clip pt-[calc(4rem+2rem)] pb-24 md:pt-[calc(4rem+3rem)]">
        <AmbientGlow position="top" intensity="medium" size={1000} />
        <AmbientGlow position="bottom-left" intensity="subtle" size={700} />
        <MeridianShortlist shortlist={shortlist} trackRecord={trackRecord} />
      </section>
      <SiteFooter />
    </main>
  );
}
