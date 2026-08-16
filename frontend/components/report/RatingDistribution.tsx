"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { chartAxisLine, chartGrid, chartLegend, chartTick, chartTooltip } from "./chartTheme";
import { shortTitle } from "./format";
import type { StructuredProduct } from "@/lib/types";

/**
 * Star-rating distribution per product (1–5★ share of ratings) — most useful
 * when a handful of products are in focus (compare / deep-dive).
 */

const STAR_BUCKETS = [
  { key: "5_star", label: "5★", color: "var(--sage)" },
  { key: "4_star", label: "4★", color: "var(--sage-soft)" },
  { key: "3_star", label: "3★", color: "var(--ink-soft)" },
  { key: "2_star", label: "2★", color: "var(--dusk)" },
  { key: "1_star", label: "1★", color: "var(--terracotta)" },
] as const;

export default function RatingDistribution({ products }: { products: StructuredProduct[] }) {
  const focused = products.filter((p) => p.reviews_histogram != null).slice(0, 5);
  if (focused.length < 2) return null;

  const rows = focused.map((product) => ({
    name: shortTitle(product.title ?? product.asin ?? "?", 20),
    ...Object.fromEntries(
      STAR_BUCKETS.map((bucket) => [bucket.key, product.reviews_histogram?.[bucket.key] ?? 0])
    ),
  }));

  return (
    <div className="chart-card">
      <h4>Rating distribution</h4>
      <p className="chart-sub">Share of ratings per product, by star</p>
      <div className="chart-frame">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={rows} margin={{ left: 0, right: 8 }}>
            <CartesianGrid vertical={false} stroke={chartGrid.stroke} strokeDasharray={chartGrid.strokeDasharray} />
            <XAxis dataKey="name" tick={chartTick} axisLine={chartAxisLine} tickLine={false} interval={0} />
            <YAxis tick={chartTick} axisLine={false} tickLine={false} />
            <Tooltip contentStyle={chartTooltip} cursor={{ fill: "var(--sage-tint)" }} />
            <Legend wrapperStyle={chartLegend} />
            {STAR_BUCKETS.map((bucket) => (
              <Bar key={bucket.key} dataKey={bucket.key} name={bucket.label} fill={bucket.color} />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
