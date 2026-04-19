from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
from pathlib import Path

from app.database import init_db
from app.routes import setup, profile, search, results, report


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Privacy Dashboard", lifespan=lifespan)

_static = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(_static)), name="static")

app.include_router(setup.router)
app.include_router(profile.router)
app.include_router(search.router)
app.include_router(results.router)
app.include_router(report.router)


@app.get("/")
async def root():
    return RedirectResponse(url="/setup")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8080, reload=True)
