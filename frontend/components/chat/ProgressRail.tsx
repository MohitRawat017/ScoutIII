"use client";

import { Check } from "lucide-react";
import { PIPELINE_STEPS } from "@/lib/constants";
import type { ProgressPayload } from "@/lib/types";

type StepStatus = "pending" | "active" | "done";

export default function ProgressRail({ seen }: { seen: ProgressPayload[] }) {
  const doneNodes = new Set(seen.map((p) => p.step));
  const lastSeen = seen.length > 0 ? seen[seen.length - 1].step : null;

  const statusFor = (node: string): StepStatus => {
    if (node === lastSeen) return "active";
    if (doneNodes.has(node)) return "done";
    return "pending";
  };

  return (
    <ol className="progress-rail">
      {PIPELINE_STEPS.map((step) => {
        const status = statusFor(step.node);
        return (
          <li
            key={step.node}
            className={`progress-pill is-${status}`}
            aria-current={status === "active" ? "step" : undefined}
          >
            <span className="pill-icon" aria-hidden="true">
              {status === "done" ? <Check /> : status === "active" ? <span className="pill-dot" /> : null}
            </span>
            <span>{step.label}</span>
          </li>
        );
      })}
    </ol>
  );
}
