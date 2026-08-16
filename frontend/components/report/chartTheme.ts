/** Shared recharts styling anchored to the studio design tokens (no hex values). */

export const chartTick = { fill: "var(--ink-soft)", fontSize: 12 } as const;

export const chartTooltip = {
  background: "var(--bg-alt)",
  border: "1px solid var(--line)",
  borderRadius: 10,
  color: "var(--ink)",
  fontSize: 13,
  padding: "8px 12px",
} as const;

export const chartAxisLine = { stroke: "var(--line)" } as const;

export const chartGrid = { stroke: "var(--line)", strokeDasharray: "3 6" } as const;

export const chartLegend = { fontSize: 13, color: "var(--ink-soft)" } as const;
