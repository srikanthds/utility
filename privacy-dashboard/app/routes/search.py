import asyncio
import logging
import uuid
from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.database import get_db
from app.services.search_engine import build_queries, search_with_fallback
from app.services.image_search import tineye_search
from app.services.breach_check import hibp_check

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))
logger = logging.getLogger(__name__)

# Keep references to running tasks so they aren't garbage-collected.
_active_scans: dict[str, asyncio.Task] = {}

QUERY_TIMEOUT = 12  # seconds per individual query


@router.get("/search", response_class=HTMLResponse)
async def search_page(request: Request):
    profile = None
    async for db in get_db():
        row = await db.execute("SELECT * FROM user_profile ORDER BY id DESC LIMIT 1")
        profile = await row.fetchone()
    if not profile:
        return RedirectResponse(url="/profile")
    return templates.TemplateResponse(request, "search.html", {"profile": profile})


@router.post("/search")
async def run_scan(request: Request):
    """Start a scan as a background task and redirect to the progress page immediately."""
    async for db in get_db():
        row = await db.execute("SELECT * FROM user_profile ORDER BY id DESC LIMIT 1")
        profile = await row.fetchone()

    if not profile:
        return RedirectResponse(url="/profile")

    profile_id = profile["id"]
    name = profile["name"]
    email = profile["email"]
    photo_path = profile["photo_path"]

    queries = build_queries(name, email)
    # Total steps = text queries + optional image search + breach check
    total_steps = len(queries) + (1 if photo_path else 0) + 1
    scan_id = uuid.uuid4().hex[:8]

    # Prepare DB: clear old results & create scan record
    async for db in get_db():
        await db.execute("DELETE FROM search_results WHERE profile_id = ?", (profile_id,))
        await db.execute(
            "INSERT INTO scans (id, profile_id, status, total_queries, completed_queries) VALUES (?, ?, 'running', ?, 0)",
            (scan_id, profile_id, total_steps),
        )
        await db.commit()

    # Cancel any already-running scan for this profile
    for sid, task in list(_active_scans.items()):
        if not task.done():
            task.cancel()
        _active_scans.pop(sid, None)

    # Fire-and-forget background task
    task = asyncio.create_task(
        _execute_scan(scan_id, profile_id, name, email, photo_path, queries)
    )
    _active_scans[scan_id] = task
    task.add_done_callback(lambda t: _active_scans.pop(scan_id, None))

    return RedirectResponse(url=f"/search/progress/{scan_id}", status_code=303)


# ── Background scan logic ──────────────────────────────────


async def _save_results(profile_id: int, results: list[dict], query_label: str) -> int:
    """Save results to DB, deduplicating against existing rows. Returns count saved."""
    if not results:
        return 0
    seen: set[str] = set()
    unique = []
    for r in results:
        url = r.get("url", "")
        if url and url not in seen:
            seen.add(url)
            unique.append(r)
    if not unique:
        return 0

    async for db in get_db():
        placeholders = ",".join("?" for _ in unique)
        cursor = await db.execute(
            f"SELECT url FROM search_results WHERE profile_id = ? AND url IN ({placeholders})",
            [profile_id] + [r["url"] for r in unique],
        )
        existing_urls = {row["url"] for row in await cursor.fetchall()}
        new_results = [r for r in unique if r["url"] not in existing_urls]
        if new_results:
            await db.executemany(
                """INSERT INTO search_results (profile_id, url, title, snippet, source, query_used)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                [
                    (profile_id, r["url"], r.get("title", ""), r.get("snippet", ""), r["source"], query_label)
                    for r in new_results
                ],
            )
            await db.commit()
        return len(new_results)


async def _bump_progress(scan_id: str) -> None:
    async for db in get_db():
        await db.execute(
            "UPDATE scans SET completed_queries = completed_queries + 1 WHERE id = ?",
            (scan_id,),
        )
        await db.commit()


async def _execute_scan(
    scan_id: str, profile_id: int, name: str, email: str,
    photo_path: str | None, queries: list[str],
) -> None:
    """Run every query sequentially, saving results after each so the UI can update live."""
    try:
        # ── Text queries (one at a time for progressive feedback) ──
        for query in queries:
            try:
                results = await asyncio.wait_for(search_with_fallback(query), timeout=QUERY_TIMEOUT)
                await _save_results(profile_id, results, query)
            except asyncio.TimeoutError:
                logger.warning("Query timed out: %s", query)
            except Exception as exc:
                logger.warning("Query failed: %s — %s", query, exc)
            await _bump_progress(scan_id)

        # ── Reverse image search ──
        if photo_path:
            try:
                img_results = await asyncio.wait_for(tineye_search(photo_path), timeout=30)
                await _save_results(profile_id, img_results, "reverse image search")
            except Exception as exc:
                logger.warning("Image search failed: %s", exc)
            await _bump_progress(scan_id)

        # ── Email breach check ──
        try:
            breach_results = await asyncio.wait_for(hibp_check(email), timeout=15)
            await _save_results(profile_id, breach_results, f"email breach: {email}")
        except Exception as exc:
            logger.warning("Breach check failed: %s", exc)
        await _bump_progress(scan_id)

        # ── Mark scan complete ──
        async for db in get_db():
            await db.execute("UPDATE scans SET status = 'done' WHERE id = ?", (scan_id,))
            await db.commit()
        logger.info("Scan %s completed", scan_id)

    except asyncio.CancelledError:
        logger.info("Scan %s cancelled", scan_id)
        async for db in get_db():
            await db.execute("UPDATE scans SET status = 'cancelled' WHERE id = ?", (scan_id,))
            await db.commit()
    except Exception as exc:
        logger.error("Scan %s crashed: %s", scan_id, exc)
        async for db in get_db():
            await db.execute("UPDATE scans SET status = 'error' WHERE id = ?", (scan_id,))
            await db.commit()


# ── Progress page & polling endpoint ───────────────────────


@router.get("/search/progress/{scan_id}", response_class=HTMLResponse)
async def search_progress(scan_id: str, request: Request):
    return templates.TemplateResponse(request, "search_progress.html", {"scan_id": scan_id})


@router.get("/search/status/{scan_id}")
async def scan_status(scan_id: str):
    """JSON endpoint polled by the progress page every 2 s."""
    scan = None
    results: list[dict] = []
    async for db in get_db():
        cursor = await db.execute("SELECT * FROM scans WHERE id = ?", (scan_id,))
        scan = await cursor.fetchone()
        if scan:
            cursor = await db.execute(
                "SELECT id, url, title, snippet, source, query_used, found_at, status "
                "FROM search_results WHERE profile_id = ? ORDER BY id ASC",
                (scan["profile_id"],),
            )
            results = [dict(r) for r in await cursor.fetchall()]

    if not scan:
        return JSONResponse({"error": "scan not found"}, status_code=404)

    return JSONResponse({
        "scan_id": scan_id,
        "status": scan["status"],
        "total": scan["total_queries"],
        "completed": scan["completed_queries"],
        "results": results,
    })
