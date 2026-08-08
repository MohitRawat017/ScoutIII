"use client";

import { ArrowDown } from "lucide-react";
import BreathingMark from "@/components/BreathingMark";
import Reveal from "@/components/Reveal";

export default function Hero({ onStart }: { onStart: () => void }) {
  return (
    <section className="hero" id="top">
      <div className="container hero-inner">
        <Reveal>
          <BreathingMark />
        </Reveal>
        <Reveal delay={80}>
          <p className="eyebrow">amazon research · made calm</p>
        </Reveal>
        <Reveal delay={160}>
          <h1 className="hero-title">Scoutii</h1>
        </Reveal>
        <Reveal delay={240}>
          <p className="hero-sub">
            A conversational agent for Amazon product research and competitive analysis.
            Ask a natural-language question and get a grounded market report in under a minute.
          </p>
        </Reveal>
        <Reveal delay={320}>
          <div className="hero-cta">
            <a className="btn btn-primary" href="#chat" onClick={onStart}>
              Start a research query
            </a>
            <a className="btn btn-ghost" href="#intents">
              How it works
            </a>
          </div>
        </Reveal>
        <Reveal delay={400}>
          <p className="hero-note">First report free · grounded in live Amazon data · no login needed</p>
        </Reveal>
      </div>

      <a className="scroll-cue" href="#intents" aria-label="Scroll to how it works">
        <span className="scroll-cue-label">scroll</span>
        <ArrowDown aria-hidden="true" />
      </a>
    </section>
  );
}
