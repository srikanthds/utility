from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from dotenv import set_key

from app.config import settings, get_api_status, reload_settings, ENV_FILE

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

SERVICE_INFO = {
    "google": {
        "name": "Google Custom Search",
        "description": "Deep web search for name & email mentions",
        "free_tier": "100 queries/day",
        "signup_url": "https://console.developers.google.com",
        "signup_label": "console.developers.google.com",
        "api_keys": [
            {"field": "google_api_key", "env": "GOOGLE_API_KEY", "label": "API Key", "placeholder": "AIza..."},
            {"field": "google_cx", "env": "GOOGLE_CX", "label": "Search Engine ID (CX)", "placeholder": "017..."},
        ],
    },
    "serpapi": {
        "name": "SerpAPI",
        "description": "Alternative search engine aggregator",
        "free_tier": "100 searches/month",
        "signup_url": "https://serpapi.com/users/sign_up",
        "signup_label": "serpapi.com",
        "api_keys": [
            {"field": "serpapi_key", "env": "SERPAPI_KEY", "label": "API Key", "placeholder": "your-serpapi-key"},
        ],
    },
    "tineye": {
        "name": "TinEye",
        "description": "Reverse image search for your photo",
        "free_tier": "150 searches/month",
        "signup_url": "https://services.tineye.com/TinEyeAPI",
        "signup_label": "tineye.com/api",
        "api_keys": [
            {"field": "tineye_api_key", "env": "TINEYE_API_KEY", "label": "API Key", "placeholder": "your-tineye-key"},
            {"field": "tineye_api_secret", "env": "TINEYE_API_SECRET", "label": "API Secret", "placeholder": "your-tineye-secret"},
        ],
    },
    "hibp": {
        "name": "HaveIBeenPwned",
        "description": "Email breach & data leak detection",
        "free_tier": "Paid (£3.50/mo) — skippable",
        "signup_url": "https://haveibeenpwned.com/API/Key",
        "signup_label": "haveibeenpwned.com/API",
        "api_keys": [
            {"field": "hibp_api_key", "env": "HIBP_API_KEY", "label": "API Key", "placeholder": "your-hibp-key"},
        ],
    },
}


@router.get("/setup", response_class=HTMLResponse)
async def setup_page(request: Request):
    api_status = await get_api_status()
    all_ok = all(s in ("ok", "skipped") for k, s in api_status.items() if k != "duckduckgo")
    return templates.TemplateResponse(
        request,
        "setup.html",
        {
            "api_status": api_status,
            "service_info": SERVICE_INFO,
            "settings": settings,
            "all_ok": all_ok,
        },
    )


@router.post("/setup/continue")
async def continue_from_setup():
    return RedirectResponse(url="/profile", status_code=303)


@router.post("/setup/save-key")
async def save_key(
    service: str = Form(...),
    google_api_key: str = Form(""),
    google_cx: str = Form(""),
    serpapi_key: str = Form(""),
    tineye_api_key: str = Form(""),
    tineye_api_secret: str = Form(""),
    hibp_api_key: str = Form(""),
):
    # Ensure .env file exists
    if not ENV_FILE.exists():
        ENV_FILE.write_text("")

    key_map = {
        "google": [("GOOGLE_API_KEY", google_api_key), ("GOOGLE_CX", google_cx)],
        "serpapi": [("SERPAPI_KEY", serpapi_key)],
        "tineye": [("TINEYE_API_KEY", tineye_api_key), ("TINEYE_API_SECRET", tineye_api_secret)],
        "hibp": [("HIBP_API_KEY", hibp_api_key)],
    }

    for env_var, value in key_map.get(service, []):
        if value.strip():
            set_key(str(ENV_FILE), env_var, value.strip())
            # Also unset the skip flag if saving a real key
            set_key(str(ENV_FILE), f"SKIP_{service.upper()}", "false")

    reload_settings()
    return RedirectResponse(url="/setup", status_code=303)


@router.post("/setup/skip")
async def skip_service(service: str = Form(...)):
    if not ENV_FILE.exists():
        ENV_FILE.write_text("")
    set_key(str(ENV_FILE), f"SKIP_{service.upper()}", "true")
    reload_settings()
    return RedirectResponse(url="/setup", status_code=303)


@router.post("/setup/unskip")
async def unskip_service(service: str = Form(...)):
    if not ENV_FILE.exists():
        ENV_FILE.write_text("")
    set_key(str(ENV_FILE), f"SKIP_{service.upper()}", "false")
    reload_settings()
    return RedirectResponse(url="/setup", status_code=303)
