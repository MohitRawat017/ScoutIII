# Scoutii Frontend

The web app for the Scoutii research agent: a Next.js studio with a landing
page, a chat workspace that streams live research progress, and structured
report views — sentiment charts, rating distribution, price-vs-rating scatter,
a sortable comparison table and insight cards. The full Markdown report stays
available in a collapsed section for when you want the detail.

Talks to the Python backend (`backend/` + `main.py`) at `POST /api/v1/chat`.

## Commands

```bash
npm ci         # install dependencies (from the lockfile)
npm run dev    # dev server on http://localhost:3000
npm run lint   # ESLint
npm run build  # production build
```

## Environment

Set the backend base URL in `.env.local` (see `.env.local.example`):

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Defaults to `http://localhost:8000` if unset — the address `uv run python
main.py` serves from the repo root.

## Stack

Next.js 16 (App Router) · React 19 · Tailwind CSS 4 · TypeScript ·
recharts · @microsoft/fetch-event-source

Architecture and the agent pipeline: root [README](../README.md).
