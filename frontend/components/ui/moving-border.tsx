"use client";

import { cn } from "@/lib/utils";
import { motion } from "motion/react";
import type { ComponentPropsWithoutRef } from "react";

type MovingBorderProps = ComponentPropsWithoutRef<"div"> & {
  borderRadius?: string;
  duration?: number;
  borderClassName?: string;
  containerClassName?: string;
  as?: React.ElementType;
};

export function MovingBorder({
  children,
  duration = 2000,
  borderRadius = "1.75rem",
  borderClassName,
  containerClassName,
  className,
  as: Component = "div",
  ...props
}: MovingBorderProps) {
  return (
    <Component
      className={cn(
        "relative overflow-hidden bg-transparent p-[1px]",
        containerClassName
      )}
      style={{ borderRadius }}
      {...props}
    >
      <div
        className="absolute inset-0"
        style={{ borderRadius }}
      >
        <motion.div
          className={cn(
            "absolute inset-[-100%] h-[300%] w-[300%]",
            borderClassName
          )}
          style={{
            background:
              "conic-gradient(from 0deg, transparent 0 340deg, #8B5CF6 360deg)",
          }}
          animate={{ rotate: 360 }}
          transition={{
            duration: duration / 1000,
            repeat: Infinity,
            ease: "linear",
          }}
        />
      </div>
      <div
        className={cn(
          "relative z-10 bg-background",
          className
        )}
        style={{ borderRadius: `calc(${borderRadius} - 1px)` }}
      >
        {children}
      </div>
    </Component>
  );
}
