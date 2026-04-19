import aiosqlite
from pathlib import Path
from typing import AsyncGenerator
from app.config import settings

_DB_PATH = Path(settings.DB_PATH)


async def get_db() -> AsyncGenerator[aiosqlite.Connection, None]:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(_DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        yield db


async def init_db() -> None:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(_DB_PATH) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS user_profile (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT    NOT NULL,
                email       TEXT    NOT NULL,
                photo_path  TEXT,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS search_results (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id    INTEGER NOT NULL,
                url           TEXT    NOT NULL,
                title         TEXT,
                snippet       TEXT,
                source        TEXT    NOT NULL,
                query_used    TEXT,
                found_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status        TEXT    DEFAULT 'pending',
                removal_draft TEXT,
                FOREIGN KEY (profile_id) REFERENCES user_profile(id)
            );

            CREATE TABLE IF NOT EXISTS scans (
                id                TEXT    PRIMARY KEY,
                profile_id        INTEGER NOT NULL,
                status            TEXT    DEFAULT 'running',
                total_queries     INTEGER DEFAULT 0,
                completed_queries INTEGER DEFAULT 0,
                started_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (profile_id) REFERENCES user_profile(id)
            );
        """)
        await db.commit()
