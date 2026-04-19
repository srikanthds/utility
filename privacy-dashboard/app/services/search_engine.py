import asyncio
from typing import Any, Dict, List

import httpx
from app.config import settings

SEARCH_TIMEOUT_SECONDS = 5
DDG_TIMEOUT_SECONDS = 5
MAX_QUERY_CONCURRENCY = 3


async def google_search(query: str, num: int = 10) -> List[Dict]:
    if settings.SKIP_GOOGLE or not settings.GOOGLE_API_KEY or not settings.GOOGLE_CX:
        return []
    try:
        async with httpx.AsyncClient(timeout=SEARCH_TIMEOUT_SECONDS) as client:
            r = await client.get(
                "https://www.googleapis.com/customsearch/v1",
                params={"key": settings.GOOGLE_API_KEY, "cx": settings.GOOGLE_CX, "q": query, "num": num},
            )
            if r.status_code != 200:
                return []
            return [
                {"url": i.get("link", ""), "title": i.get("title", ""), "snippet": i.get("snippet", ""), "source": "google"}
                for i in r.json().get("items", [])
            ]
    except Exception:
        return []


async def serpapi_search(query: str, num: int = 10) -> List[Dict]:
    if settings.SKIP_SERPAPI or not settings.SERPAPI_KEY:
        return []
    try:
        async with httpx.AsyncClient(timeout=SEARCH_TIMEOUT_SECONDS) as client:
            r = await client.get(
                "https://serpapi.com/search",
                params={"api_key": settings.SERPAPI_KEY, "q": query, "num": num, "engine": "google"},
            )
            if r.status_code != 200:
                return []
            return [
                {"url": i.get("link", ""), "title": i.get("title", ""), "snippet": i.get("snippet", ""), "source": "serpapi"}
                for i in r.json().get("organic_results", [])
            ]
    except Exception:
        return []


def _ddg_search_sync(query: str, num: int) -> List[Dict]:
    try:
        from ddgs import DDGS

        with DDGS(timeout=DDG_TIMEOUT_SECONDS) as ddgs:
            hits = ddgs.text(query, max_results=num) or []
        return [
            {"url": h.get("href", ""), "title": h.get("title", ""), "snippet": h.get("body", ""), "source": "duckduckgo"}
            for h in hits
        ]
    except Exception:
        return []


async def ddg_search(query: str, num: int = 10) -> List[Dict]:
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(_ddg_search_sync, query, num),
            timeout=DDG_TIMEOUT_SECONDS + 1,
        )
    except asyncio.TimeoutError:
        return []


async def search_with_fallback(query: str) -> List[Dict]:
    """Try Google → SerpAPI → DuckDuckGo, return first non-empty results."""
    results = await google_search(query)
    if results:
        return results
    results = await serpapi_search(query)
    if results:
        return results
    return await ddg_search(query)


async def search_query_with_timeout(query: str) -> List[Dict[str, Any]]:
    try:
        return await asyncio.wait_for(search_with_fallback(query), timeout=SEARCH_TIMEOUT_SECONDS + DDG_TIMEOUT_SECONDS + 2)
    except asyncio.TimeoutError:
        return []


def build_queries(name: str, email: str) -> List[str]:
    return [
        f'"{name}"',
        f'"{email}"',
        f'"{name}" email',
        f'"{name}" contact',
        f'"{name}" site:facebook.com',
        f'"{name}" site:linkedin.com',
        f'"{name}" site:twitter.com',
        f'"{name}" site:instagram.com',
        f'"{name}" site:reddit.com',
        f'"{name}" -site:linkedin.com -site:facebook.com',
    ]
