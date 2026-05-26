import { cn } from "@/lib/utils";

interface MeridianWordmarkProps {
  /** Height (font-size) in pixels */
  height?: number;
  className?: string;
}

/**
 * "MERIDIAN" wordmark — set in the heading face at black weight with tight
 * tracking to sit alongside the radar-"M" mark. The trailing "N" carries a
 * violet tint as a quiet nod to the brand accent.
 */
export function MeridianWordmark({
  height = 20,
  className,
}: MeridianWordmarkProps) {
  return (
    <span
      className={cn(
        "font-heading font-black uppercase leading-none text-foreground",
        className,
      )}
      style={{
        fontSize: height,
        letterSpacing: "-0.03em",
      }}
    >
      Meridia<span className="text-violet-400">n</span>
    </span>
  );
}
