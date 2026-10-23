# Contributing to Scoutii

Thanks for taking the time to contribute. This covers the minimum you need to
get the project running and land a change.

## Dev environment

1. Install [uv](https://docs.astral.sh/uv/) and Python 3.12 (see `.python-version`).
2. Install Node.js 20.9+ for the web frontend (Node 22 LTS recommended).
3. Install dependencies:
   ```bash
   uv sync
   ```
4. Copy `.env.example` to `.env` and fill in your keys:
   ```
   SERPAPI_KEY=your_serpapi_key
   GEMINIAPI_KEY=your_gemini_api_key
   ```
   Never commit `.env` or expose keys in logs.

## Running the project

```bash
# FastAPI server (chat API on :8000) — what the web frontend talks to
uv run python main.py

# LangGraph dev server + Studio UI
uv run langgraph dev

# Web frontend on :3000
cd frontend
cp .env.local.example .env.local
npm ci
npm run dev
```

## Code style

Lint and format with ruff before every commit:

```bash
uv run ruff check backend/ main.py
uv run ruff format backend/ main.py
```

## Tests

```bash
uv run pytest
```

The suite covers nodes, tools, the resilience layer and the full graph
(unit + integration; every external call is mocked, no keys needed). CI runs
it with coverage, alongside ruff and the frontend lint + build.

## Commits and pull requests

- Branch from `main` using prefixes: `feat/`, `fix/`, `chore/`, `docs/`, `refactor/`.
- Conventional Commit messages, e.g. `feat(nodes): ...`, `fix(tools): ...`.
- One logical change per PR, and keep CI green.
