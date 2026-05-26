"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  AnimatePresence,
  motion,
  useMotionValueEvent,
  useScroll,
} from "motion/react";
import { Menu03Icon, ArrowUpRight01Icon, ArrowLeft01Icon } from "hugeicons-react";

import { MeridianWordmark } from "@/components/ui/meridian-wordmark";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

// All nav links use absolute + hash paths so they work cross-page. From /demo,
// clicking "Track Record" navigates to / and scrolls to #protocol; from / it's
// a same-page smooth scroll handled by the global scroll-padding-top offset.
const NAV_LINKS = [
  { label: "Track Record", href: "/#protocol" },
  { label: "How It Works", href: "/#lifecycle" },
  { label: "The Swarm", href: "/#use-cases" },
  { label: "Docs", href: "#" },
];

const spring = { type: "spring" as const, stiffness: 260, damping: 32 };

export function SiteNavbar() {
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const { scrollY } = useScroll();
  const pathname = usePathname();
  const isAppPage = pathname === "/demo";

  useMotionValueEvent(scrollY, "change", (latest) => {
    setScrolled(latest > 24);
  });

  return (
    <header className="fixed inset-x-0 top-0 z-50 flex flex-col items-center">
      <motion.div
        initial={false}
        animate={{
          width: scrolled ? "94%" : "100%",
          maxWidth: scrolled ? 880 : 1440,
          marginTop: scrolled ? 14 : 0,
          borderRadius: scrolled ? 999 : 0,
          paddingLeft: scrolled ? 10 : 0,
          paddingRight: scrolled ? 10 : 0,
        }}
        transition={spring}
        className={cn(
          "relative overflow-hidden border backdrop-blur-2xl",
          scrolled
            ? "border-white/10 bg-[rgba(10,10,10,0.55)] shadow-[0_24px_60px_-30px_rgba(139,92,246,0.45),inset_0_1px_0_rgba(255,255,255,0.08)]"
            : "border-transparent border-b-white/5 bg-background/70",
        )}
      >
        {/* Inner violet atmosphere (visible when scrolled) */}
        <motion.div
          aria-hidden
          initial={false}
          animate={{ opacity: scrolled ? 1 : 0 }}
          transition={{ duration: 0.4 }}
          className="pointer-events-none absolute inset-0"
        >
          <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-violet-400/30 to-transparent" />
          <div className="absolute -top-16 left-1/2 size-48 -translate-x-1/2 rounded-full bg-[radial-gradient(circle,rgba(139,92,246,0.22),transparent_70%)] blur-2xl" />
        </motion.div>

        <div
          className={cn(
            "relative flex items-center justify-between transition-[height,padding] duration-300",
            scrolled ? "h-14 px-5 md:px-6" : "h-16 px-6 md:px-10",
          )}
        >
          <Link
            href="/"
            className="group flex items-center gap-2.5"
            aria-label="Meridian home"
          >
            <MeridianWordmark height={22} />
            {!isAppPage && (
              <span className="ml-2 hidden items-center gap-1.5 rounded-full border border-violet-500/25 bg-violet-500/[0.06] px-2.5 py-[3px] md:inline-flex">
                <span className="relative flex size-1">
                  <span className="absolute inline-flex size-full animate-ping rounded-full bg-violet-400 opacity-70" />
                  <span className="relative inline-flex size-1 rounded-full bg-violet-400" />
                </span>
                <span className="font-mono text-[9px] font-medium uppercase tracking-[0.22em] text-violet-200">
                  Live
                </span>
              </span>
            )}
          </Link>

          <nav className="absolute left-1/2 hidden -translate-x-1/2 items-center gap-1 md:flex">
            {NAV_LINKS.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="rounded-full px-3.5 py-1.5 text-[13px] font-medium tracking-tight text-zinc-300 transition-all duration-200 hover:bg-white/[0.06] hover:text-white"
              >
                {link.label}
              </Link>
            ))}
          </nav>

          <div className="flex items-center gap-2">
            {/* ⌘K keyboard shortcut hint — premium app signal, landing only */}
            {!isAppPage && (
              <div className="mr-1 hidden items-center gap-1 rounded-md border border-white/10 bg-white/[0.04] px-2 py-1 lg:inline-flex">
                <kbd className="font-mono text-[10px] font-medium text-zinc-400">
                  ⌘
                </kbd>
                <kbd className="font-mono text-[10px] font-medium text-zinc-400">
                  K
                </kbd>
              </div>
            )}
            {/* CTA — Launch App on landing, Back home on /demo. Using
                AnimatePresence so the swap is a smooth cross-fade instead
                of a hard unmount. */}
            <AnimatePresence mode="wait" initial={false}>
              {isAppPage ? (
                <motion.div
                  key="back-home"
                  initial={{ opacity: 0, x: 8 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -8 }}
                  transition={{ duration: 0.2 }}
                  whileHover={{ scale: 0.97 }}
                  whileTap={{ scale: 0.94 }}
                >
                  <Link href="/">
                    <Button
                      variant="outline"
                      size="pill"
                      className="hidden md:inline-flex"
                    >
                      <ArrowLeft01Icon className="size-3.5" strokeWidth={2.2} />
                      Back to Site
                    </Button>
                  </Link>
                </motion.div>
              ) : (
                <motion.div
                  key="launch-app"
                  initial={{ opacity: 0, x: 8 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -8 }}
                  transition={{ duration: 0.2 }}
                  whileHover={{ scale: 0.97 }}
                  whileTap={{ scale: 0.94 }}
                >
                  <Link href="/demo">
                    <Button
                      variant="violet"
                      size="pill"
                      className="hidden md:inline-flex"
                    >
                      See Today&apos;s Picks
                      <ArrowUpRight01Icon className="size-3.5" strokeWidth={2.2} />
                    </Button>
                  </Link>
                </motion.div>
              )}
            </AnimatePresence>
            <button
              type="button"
              onClick={() => setOpen((v) => !v)}
              aria-label="Toggle menu"
              className="inline-flex size-9 cursor-pointer items-center justify-center rounded-lg border border-white/10 bg-white/5 text-foreground md:hidden"
            >
              <Menu03Icon className="size-4" />
            </button>
          </div>
        </div>

      </motion.div>

      {/* Mobile drawer — sibling to the nav pill so it's not clipped by
          rounded-full or overflow-hidden when the header is in its scrolled
          pill state. Uses AnimatePresence for a smooth slide-down. */}
      <AnimatePresence>
        {open && (
          <motion.div
            key="mobile-drawer"
            initial={{ opacity: 0, y: -8, height: 0 }}
            animate={{ opacity: 1, y: 0, height: "auto" }}
            exit={{ opacity: 0, y: -8, height: 0 }}
            transition={{ type: "spring", stiffness: 300, damping: 32 }}
            className="mx-4 mt-2 w-[calc(100%-2rem)] max-w-[880px] overflow-hidden rounded-2xl border border-white/10 bg-[rgba(10,10,10,0.92)] shadow-[0_24px_60px_-24px_rgba(139,92,246,0.35)] backdrop-blur-2xl md:hidden"
          >
            <div className="flex flex-col gap-1 p-6">
              {NAV_LINKS.map((link, i) => (
                <motion.div
                  key={link.href}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.05 + i * 0.04 }}
                >
                  <Link
                    href={link.href}
                    onClick={() => setOpen(false)}
                    className="block rounded-lg px-3 py-2.5 text-[15px] font-medium tracking-tight text-zinc-300 transition-colors hover:bg-white/[0.06] hover:text-white"
                  >
                    {link.label}
                  </Link>
                </motion.div>
              ))}
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.05 + NAV_LINKS.length * 0.04 }}
                className="mt-2 border-t border-white/5 pt-4"
              >
                <Link
                  href={isAppPage ? "/" : "/demo"}
                  onClick={() => setOpen(false)}
                >
                  <Button
                    variant={isAppPage ? "outline" : "violet"}
                    size="pill"
                    className="w-full justify-center"
                  >
                    {isAppPage ? (
                      <>
                        <ArrowLeft01Icon
                          className="size-3.5"
                          strokeWidth={2.2}
                        />
                        Back to Site
                      </>
                    ) : (
                      <>
                        See Today&apos;s Picks
                        <ArrowUpRight01Icon
                          className="size-3.5"
                          strokeWidth={2.2}
                        />
                      </>
                    )}
                  </Button>
                </Link>
              </motion.div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
