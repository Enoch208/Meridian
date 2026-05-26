"use client";

import { Button as ButtonPrimitive } from "@base-ui/react/button";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex shrink-0 cursor-pointer items-center justify-center border font-mono text-xs uppercase tracking-widest transition-none outline-none select-none disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-40 [&_svg]:pointer-events-none [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        default:
          "border-white/10 bg-white text-zinc-900 hover:bg-zinc-100",
        violet:
          "border-violet-400/40 bg-violet-500 text-white hover:bg-violet-400 hover:border-violet-300/60",
        outline:
          "border-white/15 bg-transparent text-zinc-100 hover:bg-white/5 hover:border-white/25",
        ghost:
          "border-transparent bg-transparent text-zinc-400 hover:text-zinc-100 hover:bg-white/5",
        destructive:
          "border-red-900/40 bg-transparent text-red-400 hover:bg-red-900/20",
      },
      size: {
        default: "h-9 gap-2 px-5",
        sm: "h-7 gap-1.5 px-3 text-[10px]",
        lg: "h-11 gap-2.5 px-6 text-[11px]",
        pill: "h-10 gap-2 rounded-full px-6 text-[11px]",
        icon: "h-9 w-9",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

function Button({
  className,
  variant = "default",
  size = "default",
  ...props
}: ButtonPrimitive.Props & VariantProps<typeof buttonVariants>) {
  return (
    <ButtonPrimitive
      data-slot="button"
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  );
}

export { Button, buttonVariants };
