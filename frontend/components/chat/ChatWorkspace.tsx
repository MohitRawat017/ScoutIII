"use client";

import { useCallback, useRef, useState } from "react";
import { Square } from "lucide-react";

import { streamChat } from "@/lib/api";
import type { ChatPhase, DataPayload, ProgressPayload } from "@/lib/types";
import QueryForm from "./QueryForm";
import ProgressRail from "./ProgressRail";
import StructuredReport from "@/components/report/StructuredReport";
import ReportSkeleton from "@/components/report/ReportSkeleton";
import WarningsBanner from "./WarningsBanner";
import UsageChip from "./UsageChip";
import ErrorState from "./ErrorState";
import EmptyState from "./EmptyState";

export default function ChatWorkspace({
  draft,
  onDraftChange,
}: {
  draft: string;
  onDraftChange: (value: string) => void;
}) {
  const [phase, setPhase] = useState<ChatPhase>("idle");
  const [progress, setProgress] = useState<ProgressPayload[]>([]);
  const [report, setReport] = useState<DataPayload | null>(null);
  const [error, setError] = useState("");
  const [retryAfter, setRetryAfter] = useState(30);
  const [lastQuery, setLastQuery] = useState("");
  const abortRef = useRef<AbortController | null>(null);

  const run = useCallback(async (query: string) => {
    setLastQuery(query);
    setPhase("researching");
    setError("");
    setProgress([]);
    setReport(null);

    const controller = new AbortController();
    abortRef.current = controller;

    await streamChat(
      query,
      {
        onProgress: (p) => setProgress((prev) => [...prev, p]),
        onData: (d) => {
          setReport(d);
          setPhase("report");
        },
        onError: (message) => {
          setError(message);
          setPhase("error");
        },
        onRateLimit: (seconds) => {
          setRetryAfter(seconds);
          setPhase("rate-limited");
        },
        onDone: () => {
          setPhase((prev) => (prev === "researching" ? "idle" : prev));
        },
      },
      controller.signal
    );
    abortRef.current = null;
  }, []);

  const submit = useCallback(() => {
    const query = draft.trim();
    if (!query || phase === "researching") return;
    onDraftChange("");
    void run(query);
  }, [draft, phase, run, onDraftChange]);

  const stop = useCallback(() => abortRef.current?.abort(), []);

  const startNew = useCallback(() => {
    setPhase("idle");
    setProgress([]);
    setReport(null);
    setError("");
  }, []);

  return (
    <div className="chat-panel">
      <QueryForm value={draft} onChange={onDraftChange} onSubmit={submit} busy={phase === "researching"} />

      {phase === "idle" && !report && <EmptyState onPick={onDraftChange} />}

      {phase === "researching" && (
        <>
          <ProgressRail seen={progress} />
          <ReportSkeleton />
          <div className="research-meta">
            <span className="research-status" aria-live="polite">
              <span className="pill-dot" aria-hidden="true" />
              Researching “{lastQuery}”…
            </span>
            <button type="button" className="btn btn-ghost btn-sm" onClick={stop}>
              <Square size={13} aria-hidden="true" /> Stop
            </button>
          </div>
        </>
      )}

      {phase === "report" && report && (
        <>
          <WarningsBanner warnings={report.warnings ?? []} />
          <div className="report-head">
            <h2>Research report</h2>
            <UsageChip usage={report.usage} durationMs={report.duration_ms} />
          </div>
          <StructuredReport report={report} />
          <div className="research-meta">
            <span />
            <button type="button" className="btn btn-ghost btn-sm" onClick={startNew}>
              New research
            </button>
          </div>
        </>
      )}

      {phase === "error" && (
        <ErrorState message={error} onRetry={() => void run(lastQuery)} />
      )}

      {phase === "rate-limited" && (
        <div className="error-state" role="alert">
          <h3>You&apos;ve moved quickly</h3>
          <p>
            The backend allows a limited number of queries per minute. Please wait about{" "}
            {retryAfter} seconds before sending another one.
          </p>
        </div>
      )}
    </div>
  );
}
