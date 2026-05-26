"use client";

import { useId } from "react";
import { motion } from "motion/react";

import { cn } from "@/lib/utils";

interface MiniLineChartProps {
  data: number[];
  width?: number;
  height?: number;
  color?: string;
  strokeWidth?: number;
  className?: string;
  animate?: boolean;
}

export function MiniLineChart({
  data,
  width = 240,
  height = 80,
  color = "rgb(139, 92, 246)",
  strokeWidth = 1.75,
  className,
  animate = true,
}: MiniLineChartProps) {
  const gradientId = useId();
  const safeData = data.length > 1 ? data : [0, 1];
  const max = Math.max(...safeData);
  const min = Math.min(...safeData);
  const span = max - min || 1;

  const step = width / (safeData.length - 1);
  const points = safeData.map((value, index) => {
    const x = index * step;
    const y = height - ((value - min) / span) * (height - strokeWidth * 2) - strokeWidth;
    return { x, y };
  });

  const linePath = points
    .map((p, i) => (i === 0 ? `M ${p.x},${p.y}` : `L ${p.x},${p.y}`))
    .join(" ");

  const areaPath = `${linePath} L ${width},${height} L 0,${height} Z`;

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      preserveAspectRatio="none"
      className={cn("h-full w-full", className)}
      aria-hidden
    >
      <defs>
        <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.35" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      <motion.path
        d={areaPath}
        fill={`url(#${gradientId})`}
        initial={animate ? { opacity: 0 } : undefined}
        whileInView={animate ? { opacity: 1 } : undefined}
        viewport={animate ? { once: true, margin: "-15%" } : undefined}
        transition={animate ? { duration: 0.8, delay: 0.3 } : undefined}
      />
      <motion.path
        d={linePath}
        fill="none"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeLinejoin="round"
        initial={animate ? { pathLength: 0 } : undefined}
        whileInView={animate ? { pathLength: 1 } : undefined}
        viewport={animate ? { once: true, margin: "-15%" } : undefined}
        transition={animate ? { duration: 1.2, ease: "easeOut" } : undefined}
      />
      {/* Endpoint dot */}
      <motion.circle
        cx={points[points.length - 1].x}
        cy={points[points.length - 1].y}
        r={3}
        fill={color}
        initial={animate ? { scale: 0 } : undefined}
        whileInView={animate ? { scale: 1 } : undefined}
        viewport={animate ? { once: true, margin: "-15%" } : undefined}
        transition={animate ? { type: "spring", stiffness: 400, damping: 30, delay: 1.1 } : undefined}
      />
    </svg>
  );
}
