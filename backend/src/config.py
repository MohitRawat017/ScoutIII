import os

import serpapi
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from backend.src.cost import record_serpapi_call

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
GEMINI_API_KEY = os.getenv("GEMINIAPI_KEY")

# Valid Gemini model identifiers
GEMINI_FLASH = "gemini-3-flash-preview"  # fast — used for classification
GEMINI_PRO = "gemini-3.1-pro-preview"  # deep reasoning — used for analysis

# Resilience / cache / API-protection settings (Phase 1a)
PRODUCT_CACHE_TTL_SECONDS = int(os.getenv("PRODUCT_CACHE_TTL_SECONDS", "86400"))
SEARCH_CACHE_TTL_SECONDS = int(os.getenv("SEARCH_CACHE_TTL_SECONDS", "3600"))
CACHE_DB_PATH = os.getenv("CACHE_DB_PATH", ".cache/scoutii_cache.db")
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))
LLM_MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "3"))


def get_serpapi_client() -> serpapi.Client:
    return serpapi.Client(api_key=SERPAPI_KEY)


def get_llm(
    temperature: float = 0.1,
    streaming: bool = False,
    model_name: str = GEMINI_FLASH,
    max_retries: int = LLM_MAX_RETRIES,
) -> ChatGoogleGenerativeAI:
    # max_retries gives exponential backoff on transient Gemini failures. This
    # also covers calls made inside LangGraph's prebuilt ReAct agent, which we
    # cannot wrap in tenacity because the LLM invocation is internal to it.
    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=GEMINI_API_KEY,
        temperature=temperature,
        streaming=streaming,
        max_retries=max_retries,
    )


# ── SerpApi call wrapper with retry/backoff ────────────────────────────────────


def _is_transient_serpapi_error(exc: BaseException) -> bool:
    """Decide whether a SerpApi failure is worth retrying.

    Retry: connection/timeout errors and HTTP 5xx.
    Fail fast: HTTP 4xx (bad request, invalid key, malformed params) — those
    fail identically on every attempt.
    """
    if isinstance(exc, (serpapi.HTTPConnectionError, ConnectionError, TimeoutError, OSError)):
        return True
    status = getattr(exc, "status_code", None)
    return isinstance(status, int) and status >= 500


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception(_is_transient_serpapi_error),
    reraise=True,
)
def call_serpapi(params: dict) -> dict:
    """Single SerpApi search with bounded exponential backoff on transient errors."""
    record_serpapi_call()
    return get_serpapi_client().search(params)
