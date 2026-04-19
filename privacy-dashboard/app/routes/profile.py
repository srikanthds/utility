import shutil
from pathlib import Path
from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.database import get_db

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

PHOTOS_DIR = Path("data/photos")


@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    profile = None
    async for db in get_db():
        row = await db.execute("SELECT * FROM user_profile ORDER BY id DESC LIMIT 1")
        profile = await row.fetchone()
    return templates.TemplateResponse(request, "profile.html", {"profile": profile})


@router.post("/profile")
async def save_profile(
    name: str = Form(...),
    email: str = Form(...),
    photo: UploadFile = File(None),
):
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}

    photo_path = None
    if photo and photo.filename:
        safe_name = Path(photo.filename).name
        ext = Path(safe_name).suffix.lower()
        if ext in ALLOWED_EXTENSIONS:
            PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
            dest = PHOTOS_DIR / safe_name
            with open(dest, "wb") as f:
                shutil.copyfileobj(photo.file, f)
            photo_path = str(dest)

    async for db in get_db():
        await db.execute(
            "INSERT INTO user_profile (name, email, photo_path) VALUES (?, ?, ?)",
            (name.strip(), email.strip(), photo_path),
        )
        await db.commit()

    return RedirectResponse(url="/search", status_code=303)
