<div align="center">

# Scoutii

**A research agent for the Amazon marketplace.**

Ask a plain-English question about a product or category — get a grounded
market report with charts, a competitor table and review sentiment, streamed
live while the agent works.

[![CI](https://github.com/MohitRawat017/ScoutIII/actions/workflows/ci.yml/badge.svg)](https://github.com/MohitRawat017/ScoutIII/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-informational.svg)](LICENSE)
![Python 3.12](https://img.shields.io/badge/python-3.12-3776AB?logo=python&logoColor=white)
![Node 22](https://img.shields.io/badge/node-22-339933?logo=nodedotjs&logoColor=white)
![uv](https://img.shields.io/badge/uv-managed-de5c21?logo=uv&logoColor=white)

</div>

---

## How a query flows

```
 "compare these three yoga mats"
        │
        ▼
 ┌ query_understanding ┐   Gemini Flash reads the query and picks an intent:
 │                      │   search · analyze · compare · deep-dive
 └──────────┬───────────┘
            ▼
 ┌ react_agent ─────────┐   An autonomous tool loop searches Amazon, opens the
 │                      │   promising ASINs and pulls Amazon's AI review
 └──────────┬───────────┘   insights — capped at 8 detail fetches per request.
            ▼
 ┌ aggregation ─────────┐   Products are merged, deduped and scored; market
 │                      │   stats and revenue estimates are computed.
 └──────────┬───────────┘
            ▼
 └ analysis ────────────┘   Gemini Pro writes the report — every claim tied to
            ▼               fetched data, with intent-specific structure.
 ┌ response_formatter ──┐   Progress events and the final report stream to the
 │                      │   browser over SSE.
 └──────────────────────┘
```

## Highlights

- **Grounded, not guessed** — the LLM only ever sees fetched SerpApi data; the
  report fails soft with a partial-results notice rather than inventing facts.
- **Autonomous gathering** — a ReAct agent decides which tools to call, in what
  order, and when it has enough data. Four intents are handled without manual
  wiring.
- **Review intelligence** — Amazon's AI-synthesized review summaries: per-topic
  sentiment, mention counts and star distributions, not a 20-review sample.
- **Structured reports** — sentiment charts, rating distribution,
  price-vs-rating scatter and a sortable comparison table, plus the full
  Markdown report when you want the detail.
- **Live progress** — every pipeline step streams to the UI, so a 30-second
  research run feels like a workflow, not a spinner.
- **Built for real API budgets** — response caching, exponential backoff on
  transient failures, per-IP rate limiting, an enforced 8-product cap per
  request, and per-request cost tracking in USD.

## Quick start

You'll need Python 3.12+, [uv](https://docs.astral.sh/uv/), Node.js 20.9+
(22 LTS recommended), a [SerpApi](https://serpapi.com/) key and a
[Gemini](https://aistudio.google.com/apikey) key.

```bash
git clone https://github.com/MohitRawat017/ScoutIII.git
cd ScoutIII
uv sync

cp .env.example .env      # add SERPAPI_KEY and GEMINIAPI_KEY
```

Run the backend (serves the chat API on :8000):

```bash
uv run python main.py
```

In a second terminal, run the web app on :3000:

```bash
cd frontend
cp .env.local.example .env.local
npm ci
npm run dev
```

Open http://localhost:3000, ask something like *"analyze the espresso machine
market under $200"*, and watch the report build itself.

Prefer LangGraph Studio? `uv run langgraph dev` runs the graph on its own
dev server with the Studio UI.

## The web app

The frontend is a small Next.js studio: a landing page that explains the
agent, and a chat workspace with a live progress rail, usage/cost chips and
the structured report views. It talks to the backend over a single SSE
endpoint and renders gracefully when things fail — connection loss and
partial results both get clear states, not a hang.

## API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/chat` | POST | SSE stream: `progress` events, final `data` event, `done` |
| `/api/v1/chat/sync` | POST | Synchronous JSON chat (returns the full report) |
| `/health` | GET | Health check |

```bash
curl -N -X POST http://localhost:8000/api/v1/chat/sync \
  -H "Content-Type: application/json" \
  -d '{"message": "analyze the yoga mat market on Amazon"}'
```

The `data` event carries the Markdown answer, a `structured` block
(intent, insight lists, slim product records, market stats), token usage and
the estimated cost of the request.

## Under the hood

| Layer | Technology |
|-------|------------|
| Orchestration | LangGraph (5-node pipeline, compiled graph) |
| Reasoning | Gemini Flash (routing, tool calls) · Gemini Pro (analysis) |
| Data | SerpApi — `amazon` search + `amazon_product` engines |
| API | FastAPI + SSE (`sse-starlette`) |
| Web app | Next.js 16 (App Router) · React 19 · Tailwind CSS 4 · recharts |
| Testing | pytest (51 tests, unit + integration, coverage in CI) |
| Tooling | uv · ruff · GitHub Actions (backend + frontend jobs) |

Every external call goes through one tool layer with caching
(SQLite TTL), retries with backoff, and request scoping — JSON logs with
request ids, per-node timing and cost estimation come out of the box.

## Project layout

```
backend/src/          graph wiring, nodes, tools, API, resilience + observability
backend/tests/        unit + integration suite (pytest)
frontend/             Next.js web app (landing, chat workspace, report views)
main.py               FastAPI entry point (:8000)
langgraph.json        LangGraph Platform config
```

## License

[MIT](LICENSE)
