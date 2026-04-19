from pathlib import Path
from typing import Optional
import httpx
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    GOOGLE_API_KEY: str = ""
    GOOGLE_CX: str = ""
    SERPAPI_KEY: str = ""
    TINEYE_API_KEY: str = ""
    TINEYE_API_SECRET: str = ""
    HIBP_API_KEY: str = ""

    SKIP_GOOGLE: bool = False
    SKIP_SERPAPI: bool = False
    SKIP_TINEYE: bool = False
    SKIP_HIBP: bool = False

    DB_PATH: str = "data/privacy.db"


settings = Settings()


def reload_settings() -> None:
    global settings
    settings = Settings()


async def _test_google() -> str:
    if settings.SKIP_GOOGLE:
        return "skipped"
    if not settings.GOOGLE_API_KEY or not settings.GOOGLE_CX:
        return "missing"
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(
                "https://www.googleapis.com/customsearch/v1",
                params={"key": settings.GOOGLE_API_KEY, "cx": settings.GOOGLE_CX, "q": "test", "num": 1},
            )
            return "ok" if r.status_code == 200 else "invalid"
    except Exception:
        return "error"


async def _test_serpapi() -> str:
    if settings.SKIP_SERPAPI:
        return "skipped"
    if not settings.SERPAPI_KEY:
        return "missing"
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(
                "https://serpapi.com/account",
                params={"api_key": settings.SERPAPI_KEY},
            )
            return "ok" if r.status_code == 200 else "invalid"
    except Exception:
        return "error"


async def _test_tineye() -> str:
    if settings.SKIP_TINEYE:
        return "skipped"
    if not settings.TINEYE_API_KEY:
        return "missing"
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(
                "https://api.tineye.com/rest/remaining_searches/",
                params={"api_key": settings.TINEYE_API_KEY},
            )
            return "ok" if r.status_code == 200 else "invalid"
    except Exception:
        return "error"


async def _test_hibp() -> str:
    if settings.SKIP_HIBP:
        return "skipped"
    if not settings.HIBP_API_KEY:
        return "missing"
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(
                "https://haveibeenpwned.com/api/v3/breachedaccount/test%40example.com",
                headers={"hibp-api-key": settings.HIBP_API_KEY, "user-agent": "PrivacyDashboard/1.0"},
            )
            # 200 = found breaches, 404 = no breaches — both mean the key works
            return "ok" if r.status_code in (200, 404) else "invalid"
    except Exception:
        return "error"


async def get_api_status() -> dict:
    """Live-test each API key; returns per-service status string."""
    import asyncio
    google, serpapi, tineye, hibp = await asyncio.gather(
        _test_google(), _test_serpapi(), _test_tineye(), _test_hibp()
    )
    return {
        "google": google,
        "serpapi": serpapi,
        "tineye": tineye,
        "hibp": hibp,
        # DuckDuckGo always available
        "duckduckgo": "ok",
    }
