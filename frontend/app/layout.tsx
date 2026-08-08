import type { Metadata } from "next";
import Script from "next/script";
import { Fraunces, Figtree } from "next/font/google";

import { themeInitScript } from "@/lib/theme";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import "./globals.css";

const fraunces = Fraunces({
  variable: "--font-fraunces",
  subsets: ["latin"],
  display: "swap",
});

const figtree = Figtree({
  variable: "--font-figtree",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Scoutii — Amazon Research Agent",
  description:
    "A calm, conversational agent for Amazon product research and competitive analysis. Ask a question, get a grounded market research report in under a minute.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${fraunces.variable} ${figtree.variable}`}>
      <head>
        {/* apply saved theme before first paint (no flash) */}
        <Script id="theme-init" strategy="beforeInteractive">
          {themeInitScript}
        </Script>
      </head>
      <body>
        <Header />
        {children}
        <Footer />
      </body>
    </html>
  );
}
