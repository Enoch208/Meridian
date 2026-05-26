"use client";

import Image from "next/image";
import { motion } from "motion/react";

import { cn } from "@/lib/utils";

interface MeridianMarkProps {
  /** Square size in pixels */
  size?: number;
  /** Enable floating + sway animation (hero placement) */
  animated?: boolean;
  className?: string;
}

/**
 * Meridian brand mark — the navy radar-"M" logo seated on a refined platinum
 * app-icon tile so the navy artwork reads with full contrast against the dark
 * navy canvas. Scales cleanly from 24px (navbar) up to 160px (hero).
 *
 * Layers, bottom to top:
 *  1. Platinum tile body (white → cool steel gradient)
 *  2. Top bezel highlight (glass bevel) + inset ring for definition
 *  3. The logo artwork, padded inside the tile
 */
export function MeridianMark({
  size = 40,
  animated = false,
  className,
}: MeridianMarkProps) {
  const Tile = (
    <div
      className="relative flex size-full items-center justify-center overflow-hidden rounded-[26%] bg-gradient-to-br from-white via-[#eef1f7] to-[#d3dbe9] ring-1 ring-white/40"
      style={{
        boxShadow:
          "inset 0 1px 1px rgba(255,255,255,0.9), inset 0 -2px 6px rgba(38,53,82,0.18), 0 1px 0 rgba(255,255,255,0.06)",
      }}
    >
      {/* Top specular sheen */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-x-0 top-0 h-1/2 bg-gradient-to-b from-white/70 to-transparent"
      />
      <Image
        src="/brand/meridian-mark.png"
        alt="Meridian"
        width={size}
        height={size}
        priority
        className="relative size-[68%] object-contain"
      />
    </div>
  );

  if (!animated) {
    return (
      <div
        className={cn("inline-block", className)}
        style={{ width: size, height: size }}
      >
        {Tile}
      </div>
    );
  }

  return (
    <div
      className={cn("relative inline-block", className)}
      style={{ perspective: size * 10 }}
    >
      <motion.div
        className="relative size-full"
        style={{ transformStyle: "preserve-3d" }}
        animate={{
          y: [0, -6, 0, 6, 0],
          rotateX: [6, 8, 6, 4, 6],
          rotateY: [-5, 0, 5, 0, -5],
        }}
        transition={{
          duration: 9,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      >
        {Tile}
      </motion.div>
    </div>
  );
}
