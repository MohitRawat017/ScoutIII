"use client";

import { useEffect, useRef, useState } from "react";
import { SAMPLE_QUERIES, type SampleQuery } from "@/lib/constants";
import Reveal from "@/components/Reveal";

function QueryCard({ sample, onSelect }: { sample: SampleQuery; onSelect: (q: string) => void }) {
  const [typed, setTyped] = useState("");
  const timer = useRef<number | null>(null);
  const reduced = useRef(false);

  useEffect(() => {
    reduced.current = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    return () => {
      if (timer.current !== null) window.clearInterval(timer.current);
    };
  }, []);

  const stop = () => {
    if (timer.current !== null) {
      window.clearInterval(timer.current);
      timer.current = null;
    }
  };

  const start = () => {
    if (reduced.current) {
      setTyped(sample.query);
      return;
    }
    stop();
    let i = 0;
    timer.current = window.setInterval(() => {
      i += 1;
      setTyped(sample.query.slice(0, i));
      if (i >= sample.query.length) stop();
    }, 28);
  };

  const reset = () => {
    stop();
    setTyped("");
  };

  const finished = typed === sample.query;

  return (
    <article
      className="query-card"
      tabIndex={0}
      onMouseEnter={start}
      onMouseLeave={reset}
      onFocus={start}
      onBlur={reset}
      onClick={() => onSelect(sample.query)}
    >
      <span className="query-label">{sample.label}</span>
      <p className="query-type">
        <span className={finished ? "" : "query-caret"}>{typed}</span>
      </p>
      <p className="query-outcome">{sample.outcome}</p>
    </article>
  );
}

export default function SampleQueries({ onSelect }: { onSelect: (query: string) => void }) {
  return (
    <section className="section" id="examples">
      <div className="container">
        <Reveal>
          <p className="eyebrow">examples</p>
          <h2 className="section-title">Hover a question, try it yourself</h2>
          <p className="section-intro">
            Hover to watch the query type itself out, then click it to run it.
          </p>
        </Reveal>
        <div className="query-grid">
          {SAMPLE_QUERIES.map((sample, i) => (
            <Reveal key={sample.label} delay={i * 90}>
              <QueryCard sample={sample} onSelect={onSelect} />
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
