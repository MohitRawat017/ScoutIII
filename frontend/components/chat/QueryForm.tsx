"use client";

export default function QueryForm({
  value,
  onChange,
  onSubmit,
  busy,
}: {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  busy: boolean;
}) {
  return (
    <form
      className="query-form"
      onSubmit={(event) => {
        event.preventDefault();
        if (value.trim() && !busy) onSubmit();
      }}
    >
      <div className="query-input-row">
        <input
          id="query-input"
          className="query-input"
          type="text"
          value={value}
          placeholder="e.g. Analyze the yoga mat market on Amazon"
          onChange={(event) => onChange(event.target.value)}
          disabled={busy}
          aria-label="Research query"
          autoComplete="off"
        />
        <button className="btn btn-primary" type="submit" disabled={busy || !value.trim()}>
          {busy ? "Researching…" : "Research"}
        </button>
      </div>
    </form>
  );
}
