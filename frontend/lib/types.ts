/**
 * Types mirroring the verified backend SSE contract (backend/src/api.py).
 * See docs/architecture/coding-flow.md and skills/scoutii-frontend/SKILL.md §9.
 */

export interface ProgressPayload {
  /** internal LangGraph node name, e.g. "query_understanding" */
  step: string;
  /** human-readable status string (already includes an emoji on the backend) */
  message: string;
}

export interface UsagePayload {
  estimated_cost_usd: number;
  input_tokens: number;
  output_tokens: number;
  serpapi_calls: number;
}

export interface DataPayload {
  /** full Markdown research report */
  answer: string;
  /** node failures surfaced as a partial-results notice */
  warnings?: string[];
  usage?: Partial<UsagePayload>;
  duration_ms?: number;
}

export interface ErrorPayload {
  error: string;
}

export type ChatPhase =
  | "idle" // nothing run yet this session
  | "researching" // SSE stream is open, progress events arriving
  | "report" // a report has been received (may also show warnings)
  | "error" // backend `error` event, fetch failure, or stream interruption
  | "rate-limited"; // HTTP 429 from the backend
