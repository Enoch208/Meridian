"use client";

import { cn } from "@/lib/utils";

function seededRandom(seed: number) {
  const x = Math.sin(seed) * 10000;
  return x - Math.floor(x);
}

export function Meteors({
  count = 20,
  className,
}: {
  count?: number;
  className?: string;
}) {
  // Deterministic positions from seed, rounded to 2dp so SSR and CSR
  // produce identical strings regardless of floating-point variance.
  const meteors = Array.from({ length: count }, (_, i) => ({
    id: i,
    left: `${(seededRandom(i + 1) * 100).toFixed(2)}%`,
    delay: `${(seededRandom(i + 100) * 4).toFixed(2)}s`,
    duration: `${(seededRandom(i + 200) * 2 + 2).toFixed(2)}s`,
  }));

  return (
    <div className={cn("pointer-events-none absolute inset-0 overflow-hidden", className)}>
      {meteors.map((m) => (
        <span
          key={m.id}
          className="absolute top-0 h-0.5 w-0.5 rotate-[215deg] animate-meteor rounded-full bg-violet-500 shadow-[0_0_0_1px_#ffffff10]"
          style={{
            left: m.left,
            animationDelay: m.delay,
            animationDuration: m.duration,
          }}
        >
          <span className="absolute top-1/2 -z-10 h-px w-12 -translate-y-1/2 bg-gradient-to-r from-violet-500 to-transparent" />
        </span>
      ))}
    </div>
  );
}
