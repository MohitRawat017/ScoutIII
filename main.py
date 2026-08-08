"""
main.py — FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.src.api import router
from backend.src.logging_config import configure_logging

configure_logging()

app = FastAPI(
    title="Scoutii — Amazon Research Agent",
    description=(
        "Conversational agent for Amazon product research "
        "and competitive analysis. Powered by SerpApi + Google Gemini + LangGraph."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "scoutii-agent"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
