"use client";

import { Activity, Compass, Scale, Search } from "lucide-react";
import { INTENTS } from "@/lib/constants";
import Reveal from "@/components/Reveal";

const INTENT_ICONS = {
  search: Search,
  analyze: Activity,
  compare: Scale,
  deep_dive: Compass,
} as const;

export default function IntentCards({ onSelect }: { onSelect: (query: string) => void }) {
  return (
    <section className="section" id="intents">
      <div className="container">
        <Reveal>
          <p className="eyebrow">how it works</p>
          <h2 className="section-title">Four ways to ask</h2>
          <p className="section-intro">
            The agent reads your question, classifies its intent, then picks the right research
            path automatically — search, analysis, comparison, or a full deep-dive.
          </p>
        </Reveal>

        <div className="intent-grid">
          {INTENTS.map((intent, i) => {
            const Icon = INTENT_ICONS[intent.id as keyof typeof INTENT_ICONS] ?? Search;
            return (
              <Reveal key={intent.id} delay={i * 80}>
                <button type="button" className="intent-card" onClick={() => onSelect(intent.query)}>
                  <Icon className="intent-icon" aria-hidden="true" />
                  <h3 className="intent-title">{intent.title}</h3>
                  <p className="intent-blurb">{intent.blurb}</p>
                  <span className="intent-query">“{intent.query}”</span>
                </button>
              </Reveal>
            );
          })}
        </div>
      </div>
    </section>
  );
}
