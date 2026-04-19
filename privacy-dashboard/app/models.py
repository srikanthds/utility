from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserProfile(BaseModel):
    id: Optional[int] = None
    name: str
    email: str
    photo_path: Optional[str] = None
    created_at: Optional[datetime] = None


class SearchResult(BaseModel):
    id: Optional[int] = None
    profile_id: int
    url: str
    title: Optional[str] = None
    snippet: Optional[str] = None
    source: str
    query_used: Optional[str] = None
    found_at: Optional[datetime] = None
    status: str = "pending"
    removal_draft: Optional[str] = None
