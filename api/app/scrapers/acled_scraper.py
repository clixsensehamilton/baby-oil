"""
ACLED Conflict Data Scraper
============================
Fetches structured conflict events from ACLED (Armed Conflict Location
& Event Data Project) in oil-producing regions.

Pre-news intelligence: ACLED reports events (explosions, battles, violence)
with precise geolocation, often before mainstream media covers them.

Requires a free account at: https://acleddata.com/
Auth: OAuth 2.0 password grant (email + password).
"""

import httpx
from datetime import datetime, timedelta, timezone

from app.config import settings

ACLED_TOKEN_URL = "https://acleddata.com/oauth/token"
ACLED_API_URL = "https://acleddata.com/api/acled/read"

# Oil-relevant event types (we skip protests/riots — low supply impact)
OIL_EVENT_TYPES = [
    "Battles",
    "Explosions/Remote violence",
    "Violence against civilians",
    "Strategic developments",
]

# Oil-producing countries to monitor
OIL_COUNTRIES = [
    "Iraq",
    "Iran",
    "Libya",
    "Nigeria",
    "Saudi Arabia",
    "Yemen",
    "Syria",
    "Kuwait",
    "Sudan",
    "South Sudan",
    "Russia",
    "Venezuela",
]

# Keywords to boost relevance when found in event notes
OIL_KEYWORDS = [
    "oil", "pipeline", "refinery", "petroleum", "crude",
    "tanker", "LNG", "gas", "fuel", "terminal", "depot",
    "Hormuz", "NNPC", "Aramco", "OPEC",
]


async def _get_access_token(client: httpx.AsyncClient) -> str | None:
    """Obtain an OAuth 2.0 access token from ACLED."""
    response = await client.post(
        ACLED_TOKEN_URL,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "username": settings.ACLED_EMAIL,
            "password": settings.ACLED_PASSWORD,
            "grant_type": "password",
            "client_id": "acled",
        },
    )
    response.raise_for_status()
    return response.json().get("access_token")


async def scrape_acled(days: int = 3) -> list[dict]:
    """
    Fetch recent conflict events from ACLED in oil-producing countries.
    Returns structured events filtered for supply-relevant incidents.
    """
    if not settings.ACLED_EMAIL or not settings.ACLED_PASSWORD:
        print("[ACLED] No ACLED_EMAIL or ACLED_PASSWORD configured — skipping.")
        return []

    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    countries_param = "|".join(OIL_COUNTRIES)
    all_events = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Step 1: Get OAuth token
        try:
            token = await _get_access_token(client)
            if not token:
                print("[ACLED] Failed to obtain access token.")
                return []
        except Exception as e:
            print(f"[ACLED] Auth error: {e}")
            return []

        headers = {"Authorization": f"Bearer {token}"}

        # Step 2: Fetch events for all oil countries in one request
        try:
            params = {
                "_format": "json",
                "country": countries_param,
                "event_date": cutoff,
                "event_date_where": ">=",
                "limit": 200,
                "fields": "event_id_cnty|event_date|event_type|sub_event_type|actor1|actor2|country|admin1|location|latitude|longitude|fatalities|notes",
            }

            response = await client.get(ACLED_API_URL, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

            rows = data.get("data", data) if isinstance(data, dict) else data
            if isinstance(rows, dict):
                rows = rows.get("data", [])

        except Exception as e:
            print(f"[ACLED] Fetch error: {e}")
            return []

    for row in rows:
        event_type = row.get("event_type", "")
        if event_type not in OIL_EVENT_TYPES:
            continue

        notes = row.get("notes", "")
        fatalities = int(row.get("fatalities", 0) or 0)
        sub_type = row.get("sub_event_type", "")
        location = row.get("location", "")
        admin1 = row.get("admin1", "")
        country = row.get("country", "")
        actor1 = row.get("actor1", "")
        actor2 = row.get("actor2", "")

        # Check if event mentions oil infrastructure
        notes_lower = notes.lower()
        has_oil_keyword = any(kw in notes_lower for kw in OIL_KEYWORDS)

        # Build a descriptive headline
        headline = f"{sub_type} in {location}, {admin1}, {country}"
        if fatalities > 0:
            headline += f" — {fatalities} fatalities"

        # Parse event date
        event_time = None
        try:
            event_time = datetime.strptime(row.get("event_date", ""), "%Y-%m-%d")
        except ValueError:
            pass

        raw_content = (
            f"Event type: {event_type} / {sub_type}. "
            f"Location: {location}, {admin1}, {country}. "
            f"Actors: {actor1} vs {actor2}. "
            f"Fatalities: {fatalities}. "
            f"Details: {notes[:500]}"
        )

        # Tag oil-infrastructure events for the scorer
        if has_oil_keyword:
            raw_content += " [OIL INFRASTRUCTURE RELATED]"

        all_events.append({
            "headline": headline,
            "source": "ACLED Conflict Data",
            "source_url": None,
            "raw_content": raw_content,
            "event_time": event_time,
        })

    print(f"[ACLED] Found {len(all_events)} conflict events in oil regions.")
    return all_events
