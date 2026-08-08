/** Human-facing pipeline steps, in execution order. */
export interface PipelineStep {
  node: string;
  label: string;
}

export const PIPELINE_STEPS: PipelineStep[] = [
  { node: "query_understanding", label: "Understanding your query" },
  { node: "react_agent", label: "Searching Amazon" },
  { node: "aggregation", label: "Aggregating & scoring" },
  { node: "analysis", label: "Analyzing the market" },
  { node: "response_formatter", label: "Structuring the report" },
];

export interface Intent {
  id: string;
  title: string;
  blurb: string;
  query: string;
}

export const INTENTS: Intent[] = [
  {
    id: "search",
    title: "Search",
    blurb: "Discover what's out there and how the category is priced.",
    query: "Find the best-selling yoga mats on Amazon",
  },
  {
    id: "analyze",
    title: "Analyze",
    blurb: "Deep-dive into reviews, sentiment, and revenue estimates.",
    query: "Analyze the yoga mat market on Amazon",
  },
  {
    id: "compare",
    title: "Compare",
    blurb: "Head-to-head on price, ratings, and review velocity.",
    query: "Compare the top 3 smart water bottles on Amazon",
  },
  {
    id: "deep_dive",
    title: "Deep-dive",
    blurb: "Full market report with gaps, drivers, and opportunities.",
    query: "Deep dive into the standing desk market on Amazon",
  },
];

export interface SampleQuery {
  label: string;
  query: string;
  outcome: string;
}

export const SAMPLE_QUERIES: SampleQuery[] = [
  {
    label: "market scan",
    query: "Analyze the yoga mat market on Amazon",
    outcome: "Price ranges, average ratings, and revenue estimates across the category.",
  },
  {
    label: "competitor read",
    query: "Compare the top 3 smart water bottles on Amazon",
    outcome: "A head-to-head read of pricing, review counts, and rating distributions.",
  },
  {
    label: "gap hunting",
    query: "Deep dive into the standing desk market on Amazon",
    outcome: "Purchase drivers, common complaints, and open competitive gaps.",
  },
];
