import { SiteNavbar } from "@/components/layout/site-navbar";
import { SiteFooter } from "@/components/layout/site-footer";
import { HeroOrbit } from "@/components/blocks/hero-orbit";
import { ProtocolEcosystem } from "@/components/blocks/protocol-ecosystem";
import { AutonomousLifecycle } from "@/components/blocks/autonomous-lifecycle";
import { UseCasesGrid } from "@/components/blocks/use-cases-grid";
import { ProtocolPillars } from "@/components/blocks/protocol-pillars";
import { CTABand } from "@/components/blocks/cta-band";

export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col bg-background text-foreground">
      <SiteNavbar />
      <HeroOrbit />
      <ProtocolEcosystem />
      <AutonomousLifecycle />
      <UseCasesGrid />
      <ProtocolPillars />
      <CTABand />
      <SiteFooter />
    </main>
  );
}
