"use client";

import { SAMPLE_QUERIES } from "@/lib/constants";

export default function EmptyState({ onPick }: { onPick: (query: string) => void }) {
  return (
    <div className="empty-state">
      <h3>No research yet</h3>
      <p>Ask about any Amazon category — or start from one of these:</p>
      <div className="query-hints" style={{ marginTop: 18 }}>
        {SAMPLE_QUERIES.map((sample) => (
          <button
            key={sample.label}
            type="button"
            className="query-hint"
            onClick={() => onPick(sample.query)}
          >
            {sample.query}
          </button>
        ))}
      </div>
    </div>
  );
}
