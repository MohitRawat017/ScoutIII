import { AlertCircle, RotateCcw } from "lucide-react";

export default function ErrorState({
  message,
  onRetry,
}: {
  message: string;
  onRetry: () => void;
}) {
  return (
    <div className="error-state" role="alert">
      <span className="error-icon">
        <AlertCircle aria-hidden="true" />
      </span>
      <h3>Research didn&apos;t complete</h3>
      <p>{message}</p>
      <button type="button" className="btn btn-primary" onClick={onRetry}>
        <RotateCcw aria-hidden="true" /> Try again
      </button>
    </div>
  );
}
