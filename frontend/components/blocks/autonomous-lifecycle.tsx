"use client";

import { useRef, useState } from "react";
import {
  motion,
  useMotionValueEvent,
  useScroll,
  useTransform,
} from "motion/react";

import { AmbientGlow } from "@/components/ui/ambient-glow";
import { LifecyclePanel } from "@/components/blocks/lifecycle-panel";

const spring = { type: "spring" as const, stiffness: 400, damping: 30 };

/* ─────────────────────────────────────────────
   STEP BLOCK — left-column scroll content
   ───────────────────────────────────────────── */
function Step({
  index,
  label,
  title,
  description,
  isActive,
}: {
  index: string;
  label: string;
  title: string;
  description: string;
  isActive: boolean;
}) {
  return (
    <div className="flex min-h-[50vh] flex-col justify-center py-8 lg:min-h-[60vh]">
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-20%" }}
        transition={spring}
        className="relative"
      >
        {/* Step number + label */}
        <div className="mb-5 flex items-center gap-4">
          <div
            className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border font-mono text-xs transition-colors ${
              isActive
                ? "border-violet-400/40 bg-violet-500/15 text-violet-300"
                : "border-white/10 bg-white/5 text-zinc-600"
            }`}
          >
            {index}
          </div>
          <span
            className={`font-mono text-[10px] uppercase tracking-[0.22em] transition-colors ${
              isActive ? "text-violet-300" : "text-zinc-600"
            }`}
          >
            {label}
          </span>
          {isActive && (
            <motion.div
              layoutId="step-indicator"
              className="h-px flex-1 bg-gradient-to-r from-violet-500/60 to-transparent"
              transition={spring}
            />
          )}
        </div>

        {/* Title */}
        <h3 className="font-heading mb-6 text-3xl font-semibold leading-tight tracking-tight text-foreground md:text-4xl lg:text-5xl">
          {title}
        </h3>

        {/* Description */}
        <p className="max-w-md text-base leading-relaxed text-muted-foreground md:text-lg">
          {description}
        </p>
      </motion.div>
    </div>
  );
}

/* ─────────────────────────────────────────────
   MOBILE TERMINAL — stacked below each step
   ───────────────────────────────────────────── */
function MobileTerminal({ state }: { state: 0 | 1 | 2 }) {
  return (
    <div className="mb-16 lg:hidden">
      <LifecyclePanel activeState={state} />
    </div>
  );
}

/* ─────────────────────────────────────────────
   SCROLL-AWARE WRAPPERS
   ───────────────────────────────────────────── */
function StickyTerminalWrapper({
  scrollProgress,
}: {
  scrollProgress: ReturnType<typeof useTransform<number, number>>;
}) {
  const [activeState, setActiveState] = useState<0 | 1 | 2>(0);

  useMotionValueEvent(scrollProgress, "change", (latest) => {
    const rounded = Math.round(latest) as 0 | 1 | 2;
    setActiveState(rounded);
  });

  return <LifecyclePanel activeState={activeState} />;
}

function ScrollStep({
  step,
  index,
  scrollProgress,
}: {
  step: (typeof steps)[number];
  index: number;
  scrollProgress: ReturnType<typeof useTransform<number, number>>;
}) {
  const [isActive, setIsActive] = useState(index === 0);

  useMotionValueEvent(scrollProgress, "change", (latest) => {
    setIsActive(Math.round(latest) === index);
  });

  return (
    <Step
      index={step.index}
      label={step.label}
      title={step.title}
      description={step.description}
      isActive={isActive}
    />
  );
}

/* ─────────────────────────────────────────────
   STEP DATA
   ───────────────────────────────────────────── */
const steps = [
  {
    index: "01",
    label: "The Scan",
    title: "Watch every launch.",
    description:
      "The scouts ingest every new Solana pair the moment it appears — pulling mint authorities, liquidity, and momentum signals into a single candidate stream. No manual scanning across a dozen tabs.",
  },
  {
    index: "02",
    label: "The Score",
    title: "Grade on the rubric.",
    description:
      "Each scout grades the signal it owns; the lead synthesizes them into one composite score. Unverifiable signals are marked Unknown and down-weighted — never invented to justify a pick.",
  },
  {
    index: "03",
    label: "The Call",
    title: "Surface the few that matter.",
    description:
      "The day's top picks are ranked with their strongest reasons, the standout risk, and a one-line read — then logged with a timestamp and score to the public track record. Worth investigating, never financial advice.",
  },
];

/* ─────────────────────────────────────────────
   AUTONOMOUS LIFECYCLE — scrollytelling section
   ───────────────────────────────────────────── */
export function AutonomousLifecycle() {
  const scrollRef = useRef<HTMLElement>(null);

  const { scrollYProgress } = useScroll({
    target: scrollRef,
    offset: ["start start", "end end"],
  });

  // Balanced 30/40/30 split across the scroll range with a short dead
  // zone at the start and end so users can comfortably read the first
  // and last steps without the terminal flickering between states.
  const activeStateRaw = useTransform(
    scrollYProgress,
    [0, 0.12, 0.5, 0.88, 1],
    [0, 0, 1, 2, 2],
  );

  return (
    <section
      id="lifecycle"
      ref={scrollRef}
      className="relative overflow-clip bg-[#05060F]"
    >
      <AmbientGlow position="top-right" intensity="subtle" size={900} />

      {/* Section header */}
      <div className="relative z-10 border-y border-white/5 py-24 md:py-32">
        <div className="mx-auto max-w-7xl px-6 md:px-10">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={spring}
            className="relative text-center"
          >
            <span className="font-mono text-[10px] uppercase tracking-[0.22em] text-violet-400">
              [ Pipeline ]
            </span>
            <h2 className="font-heading mx-auto mt-4 max-w-3xl text-4xl font-semibold leading-tight tracking-tight text-foreground md:text-5xl lg:text-6xl">
              Continuous discovery.
              <br />
              <span className="bg-gradient-to-r from-sky-300 via-violet-400 to-violet-600 bg-clip-text text-transparent">
                Honest scoring.
              </span>
            </h2>
            <p className="mx-auto mt-6 max-w-2xl text-base leading-relaxed text-muted-foreground">
              Three phases, one swarm. Follow a launch from the moment it hits
              the chain to a ranked, logged call — exactly how Meridian runs the
              loop every day.
            </p>
          </motion.div>
        </div>
      </div>

      {/* Scrollytelling area */}
      <div className="relative z-10">
        <div className="mx-auto flex max-w-7xl flex-col px-6 md:px-10 lg:flex-row">
          {/* Left — scroll content */}
          <div className="w-full lg:w-1/2 lg:pr-16">
            {steps.map((step, i) => (
              <div key={step.index}>
                <ScrollStep
                  step={step}
                  index={i}
                  scrollProgress={activeStateRaw}
                />
                <MobileTerminal state={i as 0 | 1 | 2} />
              </div>
            ))}
          </div>

          {/* Right — sticky terminal (desktop only) */}
          <div className="hidden w-1/2 border-l border-white/5 pl-16 lg:block">
            <div className="sticky top-24 py-32">
              <StickyTerminalWrapper scrollProgress={activeStateRaw} />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
