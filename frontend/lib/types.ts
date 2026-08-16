/**
 * Types mirroring the verified backend SSE contract (backend/src/api.py).
 * See docs/architecture/coding-flow.md and skills/scoutii-frontend/SKILL.md §9.
 */

export interface ProgressPayload {
  /** internal LangGraph node name, e.g. "query_understanding" */
  step: string;
  /** human-readable status string (already includes an emoji on the backend) */
  message: string;
}

export interface UsagePayload {
  estimated_cost_usd: number;
  input_tokens: number;
  output_tokens: number;
  serpapi_calls: number;
}

/** Per-topic Amazon-AI review insight (products carry a list of these). */
export interface ReviewInsight {
  title?: string;
  sentiment?: string;
  mentions?: {
    total?: number;
    positive?: number;
    negative?: number;
  };
  summary?: string;
  examples?: { snippet?: string }[];
}

/** Star-rating percentages; keys map to 5★…1★. */
export interface ReviewsHistogram {
  "5_star"?: number;
  "4_star"?: number;
  "3_star"?: number;
  "2_star"?: number;
  "1_star"?: number;
}

export interface RevenueEstimate {
  asin?: string;
  title?: string;
  price?: number;
  monthly_sales_est?: number;
  monthly_revenue_est?: number;
  basis?: string;
}

/** Chart-friendly product record — mirrors `structured.products` from the backend. */
export interface StructuredProduct {
  asin: string | null;
  title: string | null;
  link: string | null;
  brand: string | null;
  rank: number | null;
  extracted_price: number | null;
  rating: number | null;
  reviews: number | null;
  bought_last_month: string | null;
  reviews_histogram: ReviewsHistogram | null;
  review_insights: ReviewInsight[] | null;
  revenue_estimate: RevenueEstimate | null;
  score: number | null;
}

export interface MarketStats {
  price_range?: { min?: number | null; max?: number | null; avg?: number | null };
  avg_rating?: number | null;
  total_reviews_analyzed?: number;
  total_products_analyzed?: number;
}

export interface StructuredPayload {
  intent?: string;
  top_purchase_drivers?: string[];
  common_complaints?: string[];
  sentiment_themes?: string[];
  competitive_gaps?: string[];
  products?: StructuredProduct[];
  market_stats?: MarketStats;
}

export interface DataPayload {
  /** full Markdown research report */
  answer: string;
  /** node failures surfaced as a partial-results notice */
  warnings?: string[];
  usage?: Partial<UsagePayload>;
  duration_ms?: number;
  structured?: StructuredPayload;
}

export interface ErrorPayload {
  error: string;
}

export type ChatPhase =
  | "idle" // nothing run yet this session
  | "researching" // SSE stream is open, progress events arriving
  | "report" // a report has been received (may also show warnings)
  | "error" // backend `error` event, fetch failure, or stream interruption
  | "rate-limited"; // HTTP 429 from the backend
