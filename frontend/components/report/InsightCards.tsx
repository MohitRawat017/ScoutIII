import type { StructuredPayload } from "@/lib/types";

/**
 * Qualitative analysis lists as scannable callout cards — these are text
 * insights, so charts would be the wrong tool. Accents: opportunities sage,
 * complaints caution.
 */

function Card({
  title,
  items,
  tone,
}: {
  title: string;
  items: string[];
  tone: "positive" | "caution" | "neutral";
}) {
  if (items.length === 0) return null;
  return (
    <div className={`insight-card is-${tone}`}>
      <h4>{title}</h4>
      <ul>
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

export default function InsightCards({ structured }: { structured: StructuredPayload }) {
  const hasAny =
    (structured.top_purchase_drivers?.length ?? 0) > 0 ||
    (structured.competitive_gaps?.length ?? 0) > 0 ||
    (structured.common_complaints?.length ?? 0) > 0;
  if (!hasAny) return null;

  return (
    <div className="insight-cards">
      <Card title="Why customers buy" items={structured.top_purchase_drivers ?? []} tone="positive" />
      <Card title="Open opportunities" items={structured.competitive_gaps ?? []} tone="positive" />
      <Card title="Common complaints" items={structured.common_complaints ?? []} tone="caution" />
    </div>
  );
}
