from pathlib import Path
from collections import OrderedDict
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.database import get_db
from app.services.removal_draft import generate_removal_draft

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

VALID_STATUSES = {"safe", "reviewed", "flagged", "pending"}


@router.get("/results", response_class=HTMLResponse)
async def results_page(request: Request, source: str = "", status: str = ""):
    profile = None
    results = []
    async for db in get_db():
        row = await db.execute("SELECT * FROM user_profile ORDER BY id DESC LIMIT 1")
        profile = await row.fetchone()

        if not profile:
            break

        query = "SELECT * FROM search_results WHERE profile_id = ?"
        params: list = [profile["id"]]
        if source:
            query += " AND source = ?"
            params.append(source)
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY found_at DESC"

        cursor = await db.execute(query, params)
        results = await cursor.fetchall()

    # Count by status for badge display
    counts = {"pending": 0, "safe": 0, "reviewed": 0, "flagged": 0}
    sources: set = set()
    grouped_results: "OrderedDict[str, list]" = OrderedDict()
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
        sources.add(r["source"])
        grouped_results.setdefault(r["source"], []).append(r)

    # Get total counts (unfiltered) for summary bar
    total_counts = {"pending": 0, "safe": 0, "reviewed": 0, "flagged": 0}
    async for db in get_db():
        if profile:
            cursor = await db.execute(
                "SELECT status, COUNT(*) as cnt FROM search_results WHERE profile_id = ? GROUP BY status",
                (profile["id"],),
            )
            for row in await cursor.fetchall():
                total_counts[row["status"]] = row["cnt"]

    return templates.TemplateResponse(
        request,
        "results.html",
        {
            "profile": profile,
            "results": results,
            "grouped_results": grouped_results,
            "total_counts": total_counts,
            "sources": sorted(sources),
            "current_source": source,
            "current_status": status,
        },
    )


@router.post("/results/{result_id}/action")
async def update_action(result_id: int, action: str = Form(...)):
    if action not in VALID_STATUSES:
        return RedirectResponse(url="/results", status_code=303)

    async for db in get_db():
        if action == "flagged":
            # Fetch the result to generate removal draft
            cursor = await db.execute("SELECT * FROM search_results WHERE id = ?", (result_id,))
            row = await cursor.fetchone()
            if row:
                profile_cursor = await db.execute(
                    "SELECT name, email FROM user_profile WHERE id = ?", (row["profile_id"],)
                )
                profile = await profile_cursor.fetchone()
                if not profile:
                    return RedirectResponse(url="/results", status_code=303)
                draft = generate_removal_draft(row["url"], profile["name"], profile["email"])
                await db.execute(
                    "UPDATE search_results SET status = ?, removal_draft = ? WHERE id = ?",
                    ("flagged", draft, result_id),
                )
        else:
            await db.execute(
                "UPDATE search_results SET status = ?, removal_draft = NULL WHERE id = ?",
                (action, result_id),
            )
        await db.commit()

    return RedirectResponse(url="/results", status_code=303)


@router.get("/results/{result_id}/draft", response_class=HTMLResponse)
async def view_draft(result_id: int, request: Request):
    result = None
    async for db in get_db():
        cursor = await db.execute("SELECT * FROM search_results WHERE id = ?", (result_id,))
        result = await cursor.fetchone()
    return templates.TemplateResponse(request, "draft.html", {"result": result})
