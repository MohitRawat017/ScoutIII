# Scoutii Frontend

Chat UI for the Scoutii Amazon research agent: a Next.js app that streams live
SSE progress events and renders the dark-console Markdown research report.

 Talks to the Python backend (`backend/` + `main.py`) at `POST /api/v1/chat`.

## Commands

```bash
npm install     # install dependencies
npm run dev     # dev server on http://localhost:3000
npm run lint    # ESLint
npm run build   # production build
```

## Environment

Set the backend base URL in `.env.local` (see `.env.local.example`):

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Defaults to `http://localhost:8000` if unset — the address `uv run python main.py`
serves from the repo root.

## More

- Architecture and agent pipeline: root [README](../README.md)
- Agent guidelines: [AGENTS.md](../AGENTS.md)
