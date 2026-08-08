# Scoutii — Amazon Research Agent

[![CI](https://github.com/MohitRawat017/ScoutII/actions/workflows/ci.yml/badge.svg)](https://github.com/MohitRawat017/ScoutII/actions/workflows/ci.yml)

A Perplexity-style conversational agent for Amazon product research and competitive analysis. It uses **LangGraph** to orchestrate a multi-step research pipeline, **Google Gemini** for reasoning, and **SerpApi** for real-time Amazon data.

## How It Works

A user submits a natural-language research query. The agent:

1. **Classifies intent** — `search`, `analyze`, `compare`, or `deep_dive` (Gemini Flash)
2. **Gathers data** — autonomously searches Amazon and fetches product details + review insights (ReAct agent + SerpApi)
3. **Aggregates** — merges, scores, and computes market stats + revenue estimates
4. **Analyzes** — generates a structured Markdown market research report (Gemini Pro)
5. **Returns** — streams progress + final report via SSE

## Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- SerpApi API key ([get one](https://serpapi.com/))
- Google Gemini API key ([get one](https://aistudio.google.com/apikey))

### Setup

1. **Clone and install:**
   ```bash
   git clone <repo-url>
   cd scoutii
   uv sync
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys:
   #   SERPAPI_KEY=your_serpapi_key
   #   GEMINIAPI_KEY=your_gemini_api_key
   ```

3. **Run the server:**
   ```bash
   uv run langgraph dev
   ```
   This starts the LangGraph dev server and opens LangGraph Studio.

   Alternatively, run the FastAPI server directly:
   ```bash
   uv run python main.py
   ```


## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/chat` | POST | SSE streaming chat (progress events → final report → done) |
| `/api/v1/chat/sync` | POST | Synchronous JSON chat (returns full report) |
| `/health` | GET | Health check |

### Example

```bash
# Sync request
curl -X POST http://localhost:8000/api/v1/chat/sync \
  -H "Content-Type: application/json" \
  -d '{"message": "analyze the yoga mat market on Amazon"}'
```

## Features

- **Intent Classification**: Classifies queries as search, analyze, compare, or deep-dive
- **Autonomous Tool-Calling**: ReAct agent decides which tools to call and in what order
- **Amazon AI Review Insights**: Uses SerpApi's structured review sentiment data (per-topic, mention counts, example snippets)
- **Revenue Estimates**: Heuristic monthly revenue calculation grounded in sales data
- **Intent-Specific Reports**: Different report structures for search, analyze, compare, and deep-dive
- **SSE Streaming**: Real-time progress updates as the agent works

## Development

```bash
# Lint
ruff check backend/
ruff format backend/

# Run tests
uv run pytest
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.12+ |
| Agent Orchestration | LangGraph |
| LLM Framework | LangChain |
| LLMs | Google Gemini Flash (fast) + Pro (analysis) |
| Data Source | SerpApi (Amazon engines) |
| API | FastAPI + SSE |
| Package Manager | uv |
| Containerization | Docker |