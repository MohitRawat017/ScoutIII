/** Truncate chart/table labels — full titles stay available in the written report. */
export function shortTitle(title: string, max = 22): string {
  return title.length > max ? `${title.slice(0, max - 1).trimEnd()}…` : title;
}

/** 45231 → "45.2K" — keeps table cells and tooltips scannable. */
export function compactNumber(value: number): string {
  return Intl.NumberFormat("en", { notation: "compact", maximumFractionDigits: 1 }).format(value);
}

/**
 * First paragraph of the Markdown answer, stripped of emphasis markers —
 * the analysis prompt guarantees the report opens with a direct answer.
 */
export function headlineFrom(markdown: string): string {
  const firstParagraph = markdown.trim().split(/\n\s*\n/)[0] ?? "";
  return firstParagraph.replace(/^#+\s*/m, "").replace(/\*\*/g, "").trim();
}
