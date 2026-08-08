import { AlertTriangle } from "lucide-react";

export default function WarningsBanner({ warnings }: { warnings: string[] }) {
  if (!warnings || warnings.length === 0) return null;
  return (
    <div className="warn-banner" role="status">
      <AlertTriangle aria-hidden="true" />
      <div>
        <strong>Partial results</strong> — a few pipeline steps had trouble. Here&apos;s what we
        could salvage: {warnings.join(" · ")}
      </div>
    </div>
  );
}
