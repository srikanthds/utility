import httpx
from typing import List, Dict
from app.config import settings


async def hibp_check(email: str) -> List[Dict]:
    """Check HaveIBeenPwned for email breaches. Returns list of breach records."""
    if settings.SKIP_HIBP or not settings.HIBP_API_KEY:
        return []
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(
                f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
                headers={
                    "hibp-api-key": settings.HIBP_API_KEY,
                    "user-agent": "PrivacyDashboard/1.0",
                },
                params={"truncateResponse": "false"},
            )
            if r.status_code == 404:
                return []  # No breaches found — good news
            if r.status_code != 200:
                return []
            breaches = r.json()
            return [
                {
                    "url": f"https://{b.get('Domain', 'unknown')}",
                    "title": f"Data breach: {b.get('Name', 'Unknown')}",
                    "snippet": (
                        f"Your email was found in the '{b.get('Name')}' breach "
                        f"({b.get('BreachDate', 'unknown date')}). "
                        f"Compromised data: {', '.join(b.get('DataClasses', []))}."
                    ),
                    "source": "hibp",
                }
                for b in breaches
            ]
    except Exception:
        return []
