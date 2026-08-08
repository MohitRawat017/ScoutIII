"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

/**
 * Renders the final Markdown report as an editorial document.
 * Tables (GFM) render as quiet ledgers — see `.report-body table` in globals.css.
 */
export default function ReportView({ markdown }: { markdown: string }) {
  return (
    <div className="report-body">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{markdown}</ReactMarkdown>
    </div>
  );
}
