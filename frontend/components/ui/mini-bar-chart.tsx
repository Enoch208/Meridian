"use client";

import { useId } from "react";
import { motion } from "motion/react";

import { cn } from "@/lib/utils";

interface MiniBarChartProps {
  data: number[];
  width?: number;
  height?: number;
  color?: string;
  className?: string;
  animate?: boolean;
}

export function MiniBarChart({
  data,
  width = 240,
  height = 80,
  color = "rgb(139, 92, 246)",
  className,
  animate = true,
}: MiniBarChartProps) {
  const gradientId = useId();
  const safeData = data.length > 0 ? data : [1];
  const max = Math.max(...safeData);
  const slotWidth = width / safeData.length;
  const barWidth = slotWidth * 0.62;
  const gap = slotWidth * 0.38;

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      preserveAspectRatio="none"
      className={cn("h-full w-full overflow-visible", className)}
      aria-hidden
    >
      <defs>
        <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.95" />
          <stop offset="100%" stopColor={color} stopOpacity="0.25" />
        </linearGradient>
      </defs>
      {safeData.map((value, index) => {
        const barHeight = Math.max((value / max) * height, 2);
        const x = index * slotWidth + gap / 2;
        const y = height - barHeight;
        return (
          <motion.rect
            key={index}
            x={x}
            width={barWidth}
            rx={1.5}
            fill={`url(#${gradientId})`}
            initial={animate ? { y: height, height: 0 } : { y, height: barHeight }}
            whileInView={animate ? { y, height: barHeight } : undefined}
            viewport={animate ? { once: true, margin: "-10%" } : undefined}
            transition={
              animate
                ? {
                    type: "spring",
                    stiffness: 180,
                    damping: 22,
                    delay: index * 0.025,
                  }
                : undefined
            }
          />
        );
      })}
    </svg>
  );
}
