"use client";

import {
  CartesianGrid,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
} from "recharts";

import { chartAxisLine, chartGrid, chartTick } from "./chartTheme";
import type { StructuredProduct } from "@/lib/types";

/**
 * Price vs rating positioning, bubble size = review count. Makes market
 * structure visible at a glance for multi-product search/analyze results.
 */

interface ScatterPoint {
  x: number;
  y: number;
  z: number;
  title: string;
}

function toPoints(products: StructuredProduct[]): ScatterPoint[] {
  return products
    .filter((p) => typeof p.extracted_price === "number" && typeof p.rating === "number")
    .map((p) => ({
      x: p.extracted_price as number,
      y: p.rating as number,
      z: p.reviews ?? 0,
      title: p.title ?? p.asin ?? "Unknown",
    }));
}

interface TooltipEntry {
  payload?: ScatterPoint;
}

function PositioningTooltip({ active, payload }: { active?: boolean; payload?: TooltipEntry[] }) {
  if (!active || !payload?.[0]?.payload) return null;
  const point = payload[0].payload;
  return (
    <div className="chart-tip">
      <strong>{point.title}</strong>
      <span>${point.x.toFixed(2)} · ★ {point.y} · {point.z.toLocaleString()} reviews</span>
    </div>
  );
}

export default function PriceRatingScatter({ products }: { products: StructuredProduct[] }) {
  const points = toPoints(products);
  if (points.length < 3) return null;

  return (
    <div className="chart-card">
      <h4>Market positioning</h4>
      <p className="chart-sub">Price vs rating — larger bubbles have more reviews</p>
      <div className="chart-frame">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ left: 0, right: 16, top: 8, bottom: 8 }}>
            <CartesianGrid stroke={chartGrid.stroke} strokeDasharray={chartGrid.strokeDasharray} />
            <XAxis
              type="number"
              dataKey="x"
              name="Price"
              unit="$"
              tick={chartTick}
              axisLine={chartAxisLine}
              tickLine={false}
            />
            <YAxis
              type="number"
              dataKey="y"
              name="Rating"
              domain={[3.5, 5]}
              tick={chartTick}
              axisLine={false}
              tickLine={false}
            />
            <ZAxis type="number" dataKey="z" range={[60, 500]} />
            <Tooltip content={<PositioningTooltip />} />
            <Scatter data={points} fill="var(--sage)" fillOpacity={0.72} />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
