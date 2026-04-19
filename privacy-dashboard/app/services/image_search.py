from pathlib import Path
from typing import List, Dict
import httpx
from app.config import settings


async def tineye_search(photo_path: str) -> List[Dict]:
    """Upload photo to TinEye API and return matches."""
    if settings.SKIP_TINEYE or not settings.TINEYE_API_KEY:
        return []

    photo = Path(photo_path)
    if not photo.exists():
        return []

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            with open(photo, "rb") as f:
                r = await client.post(
                    "https://api.tineye.com/rest/search/",
                    data={
                        "api_key": settings.TINEYE_API_KEY,
                        "api_secret": settings.TINEYE_API_SECRET,
                    },
                    files={"image": (photo.name, f, "image/jpeg")},
                )
            if r.status_code != 200:
                return []
            data = r.json()
            matches = data.get("results", {}).get("matches", [])
            results = []
            for match in matches:
                # TinEye returns backlinks list; each has url + crawl_date
                backlinks = match.get("backlinks", [])
                if backlinks:
                    for bl in backlinks:
                        results.append({
                            "url": bl.get("backlink", bl.get("url", "")),
                            "title": f"TinEye match — {match.get('domain', 'unknown site')}",
                            "snippet": f"Your image was found on {match.get('domain', 'an external site')}.",
                            "source": "tineye",
                        })
                else:
                    # Fallback: use the image_url string directly
                    img_url = match.get("image_url", "")
                    if img_url:
                        results.append({
                            "url": img_url,
                            "title": f"TinEye match — {match.get('domain', 'unknown site')}",
                            "snippet": f"Your image was found on {match.get('domain', 'an external site')}.",
                            "source": "tineye",
                        })
            return results
    except Exception:
        return []
