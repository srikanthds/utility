import csv
import io
from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from app.database import get_db

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


@router.get("/report", response_class=HTMLResponse)
async def report_page(request: Request):
    profile = None
    stats = {"total": 0, "pending": 0, "safe": 0, "reviewed": 0, "flagged": 0}
    by_source: dict = {}

    async for db in get_db():
        row = await db.execute("SELECT * FROM user_profile ORDER BY id DESC LIMIT 1")
        profile = await row.fetchone()

        if profile:
            cursor = await db.execute(
                "SELECT status, COUNT(*) as cnt FROM search_results WHERE profile_id = ? GROUP BY status",
                (profile["id"],),
            )
            for r in await cursor.fetchall():
                stats[r["status"]] = r["cnt"]
                stats["total"] += r["cnt"]

            cursor = await db.execute(
                "SELECT source, COUNT(*) as cnt FROM search_results WHERE profile_id = ? GROUP BY source",
                (profile["id"],),
            )
            for r in await cursor.fetchall():
                by_source[r["source"]] = r["cnt"]

    return templates.TemplateResponse(
        request,
        "report.html",
        {
            "profile": profile,
            "stats": stats,
            "by_source": by_source,
        },
    )


@router.get("/report/export")
async def export_csv():
    rows = []
    async for db in get_db():
        row = await db.execute("SELECT * FROM user_profile ORDER BY id DESC LIMIT 1")
        profile = await row.fetchone()
        if profile:
            cursor = await db.execute(
                "SELECT url, title, snippet, source, query_used, found_at, status FROM search_results WHERE profile_id = ? ORDER BY found_at DESC",
                (profile["id"],),
            )
            rows = await cursor.fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["URL", "Title", "Snippet", "Source", "Query Used", "Found At", "Status"])
    for r in rows:
        writer.writerow([r["url"], r["title"], r["snippet"], r["source"], r["query_used"], r["found_at"], r["status"]])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=privacy_report.csv"},
    )
