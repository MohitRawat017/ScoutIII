"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { chartAxisLine, chartGrid, chartTick, chartTooltip } from "./chartTheme";
import { shortTitle } from "./format";
import type { StructuredProduct } from "@/lib/types";

/**
 * Horizontal stacked bars of positive vs negative review-mention volume,
 * aggregated across all products by insight topic (top 8 by total mentions).
 */

interface TopicRow {
  topic: string;
  positive: number;
  negative: number;
}

function aggregateTopics(products: StructuredProduct[]): TopicRow[] {
  const byTopic = new Map<string, TopicRow>();
  for (const product of products) {
    for (const insight of product.review_insights ?? []) {
      const topic = insight.title?.trim();
      if (!topic) continue;
      const row = byTopic.get(topic) ?? { topic, positive: 0, negative: 0 };
      row.positive += insight.mentions?.positive ?? 0;
      row.negative += insight.mentions?.negative ?? 0;
      byTopic.set(topic, row);
    }
  }
  return [...byTopic.values()]
    .filter((row) => row.positive + row.negative > 0)
    .sort((a, b) => b.positive + b.negative - (a.positive + a.negative))
    .slice(0, 8)
    .map((row) => ({ ...row, topic: shortTitle(row.topic, 24) }));
}

export default function SentimentChart({ products }: { products: StructuredProduct[] }) {
  const rows = aggregateTopics(products);
  if (rows.length === 0) return null;

  return (
    <div className="chart-card">
      <h4>What customers talk about</h4>
      <p className="chart-sub">Review mentions by topic, positive vs negative</p>
      <div className="chart-frame">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={rows} layout="vertical" margin={{ left: 8, right: 16 }}>
            <CartesianGrid horizontal={false} stroke={chartGrid.stroke} strokeDasharray={chartGrid.strokeDasharray} />
            <XAxis type="number" tick={chartTick} axisLine={chartAxisLine} tickLine={false} />
            <YAxis
              type="category"
              dataKey="topic"
              width={150}
              tick={chartTick}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip contentStyle={chartTooltip} cursor={{ fill: "var(--sage-tint)" }} />
            <Bar dataKey="positive" name="Positive" stackId="mentions" fill="var(--sage)" radius={[0, 3, 3, 0]} />
            <Bar dataKey="negative" name="Negative" stackId="mentions" fill="var(--terracotta)" radius={[0, 3, 3, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
