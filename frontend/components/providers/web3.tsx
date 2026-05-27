"use client";

import { createAppKit } from "@reown/appkit/react";
import { SolanaAdapter } from "@reown/appkit-adapter-solana/react";
import { solana } from "@reown/appkit/networks";

const projectId = process.env.NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID ?? "";

// createAppKit must run in the browser. Guard with `typeof window` so it is
// skipped during SSR, and a module-level flag so it only initializes once.
let started = false;
function ensureAppKit() {
  if (started || typeof window === "undefined" || !projectId) return;
  started = true;
  createAppKit({
    adapters: [new SolanaAdapter()],
    networks: [solana],
    projectId,
    metadata: {
      name: "Meridian",
      description: "The discovery scout swarm for Solana.",
      url: window.location.origin,
      icons: [`${window.location.origin}/brand/logo-meridian.png`],
    },
    features: { analytics: false },
    themeMode: "dark",
  });
}

export function Web3Provider({ children }: { children: React.ReactNode }) {
  ensureAppKit();
  return <>{children}</>;
}
