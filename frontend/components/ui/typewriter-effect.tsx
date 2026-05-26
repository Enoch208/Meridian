"use client";

import { cn } from "@/lib/utils";
import { motion, useAnimate, useInView } from "motion/react";
import { useEffect } from "react";

export function TypewriterEffect({
  words,
  className,
  cursorClassName,
}: {
  words: { text: string; className?: string }[];
  className?: string;
  cursorClassName?: string;
}) {
  const [scope, animate] = useAnimate();
  const isInView = useInView(scope);

  useEffect(() => {
    if (isInView) {
      animate(
        "span",
        { display: "inline-block", opacity: 1 },
        {
          duration: 0.3,
          delay: (i: number) => i * 0.1,
          ease: "easeInOut",
        }
      );
    }
  }, [isInView, animate]);

  const renderWords = () => (
    <motion.div ref={scope} className="inline">
      {words.map((word, idx) => (
        <div key={`word-${idx}`} className="inline-block">
          {word.text.split("").map((char, charIdx) => (
            <motion.span
              initial={{}}
              key={`char-${charIdx}`}
              className={cn(
                "hidden text-foreground opacity-0",
                word.className
              )}
            >
              {char}
            </motion.span>
          ))}
          &nbsp;
        </div>
      ))}
    </motion.div>
  );

  return (
    <div className={cn("text-center text-base font-bold sm:text-xl md:text-3xl lg:text-5xl", className)}>
      {renderWords()}
      <motion.span
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8, repeat: Infinity, repeatType: "reverse" }}
        className={cn(
          "inline-block h-4 w-[4px] rounded-sm bg-violet-500 md:h-6 lg:h-10",
          cursorClassName
        )}
      />
    </div>
  );
}

export function TypewriterEffectSmooth({
  words,
  className,
  cursorClassName,
}: {
  words: { text: string; className?: string }[];
  className?: string;
  cursorClassName?: string;
}) {
  const renderWords = () => (
    <div>
      {words.map((word, idx) => (
        <div key={`word-${idx}`} className="inline-block">
          {word.text.split("").map((char, charIdx) => (
            <span
              key={`char-${charIdx}`}
              className={cn("text-foreground", word.className)}
            >
              {char}
            </span>
          ))}
          &nbsp;
        </div>
      ))}
    </div>
  );

  return (
    <div className={cn("flex space-x-1", className)}>
      <motion.div
        className="overflow-hidden pb-2"
        initial={{ width: "0%" }}
        whileInView={{ width: "fit-content" }}
        transition={{ duration: 2, ease: "linear", delay: 1 }}
      >
        <div className="text-xs font-bold sm:text-base md:text-xl lg:text-3xl xl:text-5xl" style={{ whiteSpace: "nowrap" }}>
          {renderWords()}
        </div>
      </motion.div>
      <motion.span
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8, repeat: Infinity, repeatType: "reverse" }}
        className={cn(
          "block h-4 w-[4px] rounded-sm bg-violet-500 sm:h-6 xl:h-12",
          cursorClassName
        )}
      />
    </div>
  );
}
