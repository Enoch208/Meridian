"use client";

import Link from "next/link";
import { motion } from "motion/react";
import { ArrowUpRight01Icon } from "hugeicons-react";

import { AmbientGlow } from "@/components/ui/ambient-glow";
import { BorderBeam } from "@/components/ui/border-beam";
import { Button } from "@/components/ui/button";

export function CTABand() {
  return (
    <section className="relative overflow-hidden py-24 md:py-32">
      <div className="relative z-10 mx-auto max-w-5xl px-6 md:px-10">
        <motion.div
          initial={{ opacity: 0, y: 32 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-15%" }}
          transition={{ type: "spring", stiffness: 300, damping: 35 }}
          className="relative overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-[#14101F] via-[#0F0D18] to-[#0A0A0A] p-12 md:p-16"
        >
          {/* Ambient glow inside the card */}
          <AmbientGlow position="center" intensity="medium" size={900} />

          {/* Border beam */}
          <BorderBeam
            size={180}
            duration={9}
            colorFrom="#A78BFA"
            colorTo="#4C1D95"
          />

          <div className="relative z-10 flex flex-col items-center text-center">
            <span className="inline-flex items-center gap-2 rounded-full border border-violet-500/30 bg-violet-500/10 px-4 py-1.5">
              <span className="size-1.5 animate-pulse rounded-full bg-violet-400" />
              <span className="font-mono text-[10px] uppercase tracking-[0.22em] text-violet-300">
                Listed · Frenzy Mode
              </span>
            </span>

            <h2 className="font-heading mt-6 max-w-3xl text-4xl font-semibold leading-[0.95] tracking-tight text-foreground sm:mt-8 md:text-5xl lg:text-6xl">
              See what the swarm
              <br />
              <span className="bg-gradient-to-r from-sky-300 via-violet-400 to-violet-600 bg-clip-text text-transparent">
                found today.
              </span>
            </h2>

            <p className="mt-6 max-w-xl text-base leading-relaxed text-muted-foreground">
              No wallet needed to look. Open the live shortlist to see today&apos;s
              ranked picks and the running track record — then hold $MRDN to
              unlock the full real-time feed.
            </p>

            <div className="mt-8 flex flex-wrap items-center justify-center gap-3 sm:mt-10">
              <motion.div whileHover={{ scale: 0.97 }} whileTap={{ scale: 0.94 }}>
                <Link href="/demo">
                  <Button variant="violet" size="pill">
                    See Today&apos;s Picks
                    <ArrowUpRight01Icon className="size-4" strokeWidth={2.2} />
                  </Button>
                </Link>
              </motion.div>
              <motion.div whileHover={{ scale: 0.97 }} whileTap={{ scale: 0.94 }}>
                <Button variant="outline" size="pill">
                  Read the Thesis
                </Button>
              </motion.div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
