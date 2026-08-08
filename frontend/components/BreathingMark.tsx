/**
 * The breathing scout mark — the hero's slow-breathing visual.
 * Pure CSS animation: 4s ease-in-out cycle, scale 1 → 1.045.
 */
export default function BreathingMark() {
  return (
    <div className="breath-mark" aria-hidden="true">
      <span className="core" />
      <span className="ring" />
    </div>
  );
}
