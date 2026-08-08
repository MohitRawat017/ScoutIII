import type { UsagePayload } from "@/lib/types";

export default function UsageChip({
  usage,
  durationMs,
}: {
  usage?: Partial<UsagePayload>;
  durationMs?: number;
}) {
  const parts: string[] = [];
  const cost = usage?.estimated_cost_usd;
  if (typeof cost === "number") {
    parts.push(`$${cost.toFixed(2)}`);
  }
  if (typeof durationMs === "number") {
    parts.push(`${(durationMs / 1000).toFixed(1)}s`);
  }
  if (typeof usage?.serpapi_calls === "number") {
    parts.push(`${usage.serpapi_calls} API calls`);
  }
  if (parts.length === 0) return null;
  return <span className="usage-chip">{parts.join(" · ")}</span>;
}
