# Contributing to Scoutii

Thanks for taking the time to contribute. This document covers the minimum you
need to get the project running and land a change. The canonical rules live in
`docs/standards/` — when in doubt, those win over this file.

## Dev Environment Setup

1. Install [uv](https://docs.astral.sh/uv/) and Python 3.12 (see `.python-version`).
2. Install dependencies:
   ```bash
   uv sync
   ```
3. Copy `.env.example` to `.env` and fill in your keys:
   ```
   SERPAPI_KEY=your_serpapi_key
   GEMINIAPI_KEY=your_gemini_api_key
   ```
   Never commit `.env` or expose keys in logs — see the core rules in `AGENTS.md`.

## Running the Project

```bash
# FastAPI server (SSE chat API) on :8000
uv run python main.py

# LangGraph dev server + Studio UI
uv run langgraph dev

# Web frontend on :3000 (expects the backend at NEXT_PUBLIC_API_URL)
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```

## Code Style

- Lint and format with Ruff before every commit (required by `docs/standards/git.md`):
  ```bash
  uv run ruff check backend/
  uv run ruff format backend/
  ```
- Conventions (naming, placement, design rules): `docs/standards/coding.md`.

## Tests

```bash
uv run pytest
```

A real test suite lands with Phase 1b (see `docs/product/roadmap.md`). Until
then, `uv run pytest` will report "no tests ran" — that is expected.

## Branches, Commits, PRs

- Branch from `main` using prefixes: `feat/`, `fix/`, `chore/`, `docs/`, `refactor/`.
- Commit messages follow Conventional Commits with repo scopes
  (`agent`, `api`, `nodes`, `tools`, `config`, `models`, `docs`, `infra`).
- One logical change per PR. Full rules: `docs/standards/git.md`.

## Phase Work

Active phase plans live in the local `plan/` folder (not committed to git).
Read the relevant `plan/phase-*.md` before starting work on a phase, and check
`docs/product/roadmap.md` for current phase status.
