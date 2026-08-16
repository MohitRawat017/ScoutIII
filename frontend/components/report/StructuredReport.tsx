"use client";

import { ChevronDown } from "lucide-react";

import ReportView from "@/components/chat/ReportView";
import type { DataPayload, StructuredProduct } from "@/lib/types";
import ComparisonTable from "./ComparisonTable";
import InsightCards from "./InsightCards";
import PriceRatingScatter from "./PriceRatingScatter";
import RatingDistribution from "./RatingDistribution";
import SentimentChart from "./SentimentChart";
import { headlineFrom } from "./format";

/**
 * Composes the visual report experience: headline → charts → comparison
 * table → qualitative cards → full Markdown (collapsed). Every section
 * guards on its own data, so a sparse result degrades gracefully instead
 * of rendering broken charts.
 */

function hasReviews(product: StructuredProduct): boolean {
  return (product.reviews ?? 0) > 0;
}

export default function StructuredReport({ report }: { report: DataPayload }) {
  const structured = report.structured ?? {};
  const products = structured.products ?? [];
  const intent = structured.intent ?? "";
  const headline = headlineFrom(report.answer);
  const multiProduct = products.filter((p) => p.extracted_price != null).length >= 3;
  const focused = intent === "compare" || intent === "deep_dive";

  return (
    <div className="report-experience">
      {headline && (
        <p className="headline-strip">{headline}</p>
      )}

      {products.length === 0 ? (
        <div className="no-results">
          <h3>No products matched this query</h3>
          <p>
            The research ran, but nothing relevant came back. Try a broader category
            (e.g. “yoga mats” instead of a specific model) — the full written
            summary below may still be useful.
          </p>
        </div>
      ) : (
        <>
          <div className="chart-grid">
            <SentimentChart products={products} />
            {focused ? (
              <RatingDistribution products={products} />
            ) : (
              multiProduct && <PriceRatingScatter products={products} />
            )}
          </div>
          {(focused || multiProduct) && products.some(hasReviews) && (
            <ComparisonTable products={products} />
          )}
        </>
      )}

      <InsightCards structured={structured} />

      <details className="report-collapsible">
        <summary>
          Full written report
          <ChevronDown size={15} aria-hidden="true" />
        </summary>
        <ReportView markdown={report.answer} />
      </details>
    </div>
  );
}
