import { cn } from "@/lib/utils";

type Position =
  | "top-left"
  | "top"
  | "top-right"
  | "left"
  | "center"
  | "right"
  | "bottom-left"
  | "bottom"
  | "bottom-right";

type Intensity = "subtle" | "medium" | "strong";

const POSITION_STYLES: Record<Position, React.CSSProperties> = {
  "top-left": { top: 0, left: 0, transform: "translate(-30%, -30%)" },
  top: { top: 0, left: "50%", transform: "translate(-50%, -40%)" },
  "top-right": { top: 0, right: 0, transform: "translate(30%, -30%)" },
  left: { top: "50%", left: 0, transform: "translate(-40%, -50%)" },
  center: { top: "50%", left: "50%", transform: "translate(-50%, -50%)" },
  right: { top: "50%", right: 0, transform: "translate(40%, -50%)" },
  "bottom-left": { bottom: 0, left: 0, transform: "translate(-30%, 30%)" },
  bottom: { bottom: 0, left: "50%", transform: "translate(-50%, 40%)" },
  "bottom-right": { bottom: 0, right: 0, transform: "translate(30%, 30%)" },
};

const INTENSITY_OPACITY: Record<Intensity, number> = {
  subtle: 0.08,
  medium: 0.15,
  strong: 0.25,
};

interface AmbientGlowProps {
  position?: Position;
  intensity?: Intensity;
  color?: string;
  size?: number;
  className?: string;
}

export function AmbientGlow({
  position = "top",
  intensity = "medium",
  color = "139, 92, 246",
  size = 800,
  className,
}: AmbientGlowProps) {
  const opacity = INTENSITY_OPACITY[intensity];
  return (
    <div
      aria-hidden
      className={cn(
        "pointer-events-none absolute z-0 rounded-full mix-blend-screen",
        className,
      )}
      style={{
        ...POSITION_STYLES[position],
        width: size,
        height: size,
        background: `radial-gradient(circle, rgba(${color}, ${opacity}) 0%, rgba(${color}, ${opacity * 0.3}) 35%, transparent 70%)`,
      }}
    />
  );
}
