/**
 * SSE client for POST /api/v1/chat.
 *
 * EventSource only supports GET, and this endpoint is POST, so we use
 * `fetch` + a ReadableStream reader and parse the `text/event-stream`
 * frames manually (per skills/scoutii-frontend/SKILL.md §11).
 */

import type { DataPayload, ProgressPayload } from "./types";

function apiBaseUrl(): string {
  const raw = process.env.NEXT_PUBLIC_API_URL;
  return (raw ?? "http://localhost:8000").replace(/\/+$/, "");
}

export interface ChatHandlers {
  onProgress: (progress: ProgressPayload) => void;
  onData: (data: DataPayload) => void;
  onError: (message: string) => void;
  onRateLimit: (retryAfterSeconds: number) => void;
  onDone: () => void;
}

function isAbort(error: unknown): boolean {
  return error instanceof DOMException && error.name === "AbortError";
}

const INTERRUPTED_MSG = "The connection was interrupted mid-research. Please try again.";

/**
 * Parses a single SSE frame (everything between two blank lines) and
 * dispatches the decoded event to `handlers`. Exported as a pure function
 * so it can be unit-tested without a network.
 */
export function parseSseFrame(frame: string, handlers: ChatHandlers): void {
  let eventName = "message";
  const dataLines: string[] = [];
  for (const rawLine of frame.replace(/\r/g, "").split("\n")) {
    if (rawLine.startsWith("event:")) eventName = rawLine.slice(6).trim();
    else if (rawLine.startsWith("data:")) dataLines.push(rawLine.slice(5).trimStart());
  }
  if (dataLines.length === 0) return;

  let payload: Record<string, unknown>;
  try {
    payload = JSON.parse(dataLines.join("\n")) as Record<string, unknown>;
  } catch {
    return; // malformed frame — ignore and keep streaming
  }

  switch (eventName) {
    case "progress":
      handlers.onProgress(payload as unknown as ProgressPayload);
      break;
    case "data":
      handlers.onData(payload as unknown as DataPayload);
      break;
    case "error":
      handlers.onError(
        typeof payload.error === "string" ? payload.error : "Something went wrong during research."
      );
      break;
    case "done":
      handlers.onDone();
      break;
    default:
      break;
  }
}

/**
 * Appends a stream chunk to the buffer, dispatches every complete SSE frame,
 * and returns the leftover (incomplete) buffer.
 *
 * CRLF line endings are normalised to LF so we can split on "\n\n"
 * regardless of the server's framing — sse-starlette emits "\r\n\r\n"
 * separators, so a bare "\n\n" split would swallow the entire stream.
 */
export function processSseChunk(
  buffer: string,
  chunk: string,
  handlers: ChatHandlers
): string {
  // Normalise the full buffer, not just the incoming chunk — a "\r\n" can
  // straddle two chunks (buffer ends in "\r", chunk starts with "\n").
  buffer = (buffer + chunk).replace(/\r\n/g, "\n");
  let index: number;
  while ((index = buffer.indexOf("\n\n")) !== -1) {
    parseSseFrame(buffer.slice(0, index), handlers);
    buffer = buffer.slice(index + 2);
  }
  return buffer;
}

/**
 * Opens the streaming chat request and dispatches SSE events to `handlers`.
 * Resolves when the stream closes (after `done`) or aborts; never throws —
 * failures are routed to `onError` so the UI can render calmly.
 */
export async function streamChat(
  message: string,
  handlers: ChatHandlers,
  signal?: AbortSignal
): Promise<void> {
  let response: Response;
  try {
    response = await fetch(`${apiBaseUrl()}/api/v1/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
      signal,
    });
  } catch (error) {
    if (isAbort(error)) {
      handlers.onDone(); // user-initiated stop — let the UI recover
      return;
    }
    handlers.onError("Couldn't reach the research agent. Is the backend running?");
    return;
  }

  if (response.status === 429) {
    let retryAfter = 30;
    try {
      const body = (await response.json()) as { detail?: { retry_after_seconds?: number } };
      const seconds = body.detail?.retry_after_seconds;
      if (typeof seconds === "number" && seconds > 0) retryAfter = seconds;
    } catch {
      /* keep default */
    }
    handlers.onRateLimit(retryAfter);
    return;
  }

  if (!response.ok || !response.body) {
    handlers.onError("The research agent returned an error. Please try again.");
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  // Track whether the stream reached a terminal event (`done` / `error`).
  // If the connection dies mid-stream without one, we surface an interruption
  // instead of leaving the UI stuck in "researching" forever.
  let sawTerminal = false;
  let sawData = false;
  const dispatch: ChatHandlers = {
    onProgress: handlers.onProgress,
    onData: (d) => {
      sawData = true;
      handlers.onData(d);
    },
    onError: (m) => {
      sawTerminal = true;
      handlers.onError(m);
    },
    onRateLimit: handlers.onRateLimit,
    onDone: () => {
      sawTerminal = true;
      handlers.onDone();
    },
  };

  try {
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer = processSseChunk(buffer, decoder.decode(value, { stream: true }), dispatch);
    }
    // flush any trailing frame without the blank-line terminator
    if (buffer.trim()) parseSseFrame(buffer, dispatch);
    // Abrupt end of stream with no terminal event and no report — interrupted.
    // (A report already received is kept; the backend always sends `done`
    // after `data` in normal operation.)
    if (!sawTerminal && !sawData) {
      handlers.onError(INTERRUPTED_MSG);
    }
  } catch (error) {
    if (isAbort(error)) {
      handlers.onDone(); // user-initiated stop — let the UI recover
      return;
    }
    handlers.onError(INTERRUPTED_MSG);
  }
}
