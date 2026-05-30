import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono, Instrument_Serif } from "next/font/google";

import { SmoothScroll } from "@/components/providers/smooth-scroll";
import { Web3Provider } from "@/components/providers/web3";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const instrumentSerif = Instrument_Serif({
  variable: "--font-instrument-serif",
  subsets: ["latin"],
  weight: "400",
  style: ["normal", "italic"],
});

const SITE_URL = "https://meridian-swarm.vercel.app";
const OG_IMAGE = {
  url: "/brand/logo-meridian.png",
  width: 1254,
  height: 1254,
  alt: "Meridian — the discovery scout swarm for Solana",
};

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: "Meridian — The Discovery Scout Swarm for Solana",
    template: "%s · Meridian",
  },
  description:
    "Meridian is a swarm of specialized scout agents that continuously scans new Solana token launches, scores each against a transparent rubric, and surfaces the few worth investigating today — with a public, running track record of every call.",
  keywords: [
    "Solana token discovery",
    "scout swarm",
    "multi-agent crypto",
    "Solana new launches",
    "token scoring rubric",
    "on-chain discovery agent",
    "Swarms Marketplace",
    "Agent Capital Markets",
    "crypto track record",
    "Solana alpha",
    "tokenized agent",
    "$MRDN",
  ],
  authors: [{ name: "Meridian" }],
  creator: "Meridian",
  publisher: "Meridian",
  applicationName: "Meridian",
  category: "Crypto",
  referrer: "origin-when-cross-origin",
  openGraph: {
    type: "website",
    url: SITE_URL,
    siteName: "Meridian",
    title: "Meridian — The Discovery Scout Swarm for Solana",
    description:
      "A swarm of scout agents that finds the few Solana launches worth investigating today — scored on a transparent rubric, with a public track record of every call.",
    locale: "en_US",
    images: [OG_IMAGE],
  },
  twitter: {
    card: "summary_large_image",
    title: "Meridian — The Discovery Scout Swarm for Solana",
    description:
      "Which Solana tokens should you even be looking at right now? Meridian's scout swarm finds them — and logs every call in public.",
    images: [OG_IMAGE.url],
    creator: "@meridian_swarm",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-image-preview": "large",
      "max-snippet": -1,
      "max-video-preview": -1,
    },
  },
  alternates: {
    canonical: SITE_URL,
  },
};

export const viewport: Viewport = {
  themeColor: "#060A16",
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

const structuredData = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": `${SITE_URL}#organization`,
      name: "Meridian",
      alternateName: "Meridian Scout Swarm",
      url: SITE_URL,
      logo: `${SITE_URL}/brand/logo-meridian.png`,
      description:
        "A swarm of specialized scout agents that discovers and scores new Solana token launches, with a public running track record.",
      foundingDate: "2026",
      sameAs: ["https://x.com/meridian_swarm"],
    },
    {
      "@type": "SoftwareApplication",
      "@id": `${SITE_URL}#software`,
      name: "Meridian",
      applicationCategory: "FinanceApplication",
      applicationSubCategory: "Crypto",
      operatingSystem: "Web",
      description:
        "Multi-agent discovery layer for Solana token launches. Three live specialized scouts scan, score, and rank new pairs against a transparent rubric — every call logged in public.",
      url: SITE_URL,
      offers: {
        "@type": "Offer",
        price: "0",
        priceCurrency: "USD",
      },
      featureList: [
        "Continuous scan of new Solana launches",
        "Four live specialized scout agents — on-chain, liquidity, momentum, smart-money",
        "Transparent composite scoring rubric",
        "Daily ranked shortlist of tokens worth investigating",
        "Public, running track record of every call",
      ],
    },
    {
      "@type": "WebSite",
      "@id": `${SITE_URL}#website`,
      url: SITE_URL,
      name: "Meridian",
      publisher: { "@id": `${SITE_URL}#organization` },
      inLanguage: "en-US",
    },
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`dark ${geistSans.variable} ${geistMono.variable} ${instrumentSerif.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        <Web3Provider>
          <SmoothScroll>{children}</SmoothScroll>
        </Web3Provider>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
        />
      </body>
    </html>
  );
}
