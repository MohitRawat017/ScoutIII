/**
 * Placeholder blocks for the report sections that will appear once data
 * arrives — shown while researching so the transition isn't a blank jump.
 * Pure CSS (see .skeleton in globals.css); respects prefers-reduced-motion.
 */
export default function ReportSkeleton() {
  return (
    <div className="report-skeleton" aria-hidden="true">
      <div className="skeleton skeleton-headline" />
      <div className="skeleton-row">
        <div className="skeleton skeleton-chart" />
        <div className="skeleton skeleton-chart" />
      </div>
      <div className="skeleton skeleton-line" />
      <div className="skeleton skeleton-line is-short" />
      <div className="skeleton skeleton-line" />
    </div>
  );
}
