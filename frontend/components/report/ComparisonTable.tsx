"use client";

import { useMemo, useState } from "react";

import { compactNumber } from "./format";
import type { StructuredProduct } from "@/lib/types";

/**
 * Sortable comparison table — more useful interactively than static Markdown
 * when several products are in play. Sort keys are the numeric columns.
 */

type SortKey = "extracted_price" | "rating" | "reviews" | "monthly_revenue_est";
type SortDir = "asc" | "desc";

const COLUMNS: { key: SortKey | null; label: string }[] = [
  { key: null, label: "Product" },
  { key: "extracted_price", label: "Price" },
  { key: "rating", label: "Rating" },
  { key: "reviews", label: "Reviews" },
  { key: "monthly_revenue_est", label: "Est. revenue/mo" },
];

function sortValue(product: StructuredProduct, key: SortKey): number {
  if (key === "monthly_revenue_est") return product.revenue_estimate?.monthly_revenue_est ?? 0;
  return (product[key] as number | null) ?? 0;
}

export default function ComparisonTable({ products }: { products: StructuredProduct[] }) {
  const [sortKey, setSortKey] = useState<SortKey>("rating");
  const [sortDir, setSortDir] = useState<SortDir>("desc");

  const sorted = useMemo(() => {
    const rows = [...products];
    rows.sort((a, b) =>
      sortDir === "asc" ? sortValue(a, sortKey) - sortValue(b, sortKey) : sortValue(b, sortKey) - sortValue(a, sortKey)
    );
    return rows;
  }, [products, sortKey, sortDir]);

  function toggle(key: SortKey) {
    if (key === sortKey) {
      setSortDir((dir) => (dir === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("desc");
    }
  }

  return (
    <div className="chart-card">
      <h4>Product comparison</h4>
      <p className="chart-sub">Click a column to sort</p>
      <div className="compare-table-wrap">
        <table className="compare-table">
          <thead>
            <tr>
              {COLUMNS.map((col) => {
                const key = col.key;
                return key ? (
                  <th
                    key={key}
                    aria-sort={sortKey === key ? (sortDir === "asc" ? "ascending" : "descending") : "none"}
                  >
                    <button type="button" onClick={() => toggle(key)}>
                      {col.label}
                      <span aria-hidden="true" className="sort-arrow">
                        {sortKey === key ? (sortDir === "asc" ? "↑" : "↓") : "↕"}
                      </span>
                    </button>
                  </th>
                ) : (
                  <th key={col.label}>{col.label}</th>
                );
              })}
            </tr>
          </thead>
          <tbody>
            {sorted.map((product) => (
              <tr key={product.asin ?? product.title}>
                <td>
                  {product.link ? (
                    <a href={product.link} target="_blank" rel="noreferrer">
                      {product.title ?? product.asin}
                    </a>
                  ) : (
                    (product.title ?? product.asin ?? "—")
                  )}
                  <span className="compare-asin">{product.asin}</span>
                </td>
                <td>
                  {typeof product.extracted_price === "number" ? `$${product.extracted_price.toFixed(2)}` : "—"}
                </td>
                <td>{typeof product.rating === "number" ? `★ ${product.rating}` : "—"}</td>
                <td>{typeof product.reviews === "number" ? compactNumber(product.reviews) : "—"}</td>
                <td>
                  {product.revenue_estimate?.monthly_revenue_est != null
                    ? `$${compactNumber(product.revenue_estimate.monthly_revenue_est)}`
                    : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
