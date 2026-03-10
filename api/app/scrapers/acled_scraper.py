"""
ACLED Conflict Data Scraper
============================
Fetches structured conflict events from ACLED (Armed Conflict Location
& Event Data Project) in oil-producing regions.

Pre-news intelligence: ACLED reports events (explosions, battles, violence)
with precise geolocation, often before mainstream media covers them.

Requires a free API key from: https://developer.acleddata.com/
"""

import httpx
from datetime import datetime, timedelta, timezone

from app.config import settings

ACLED_API_URL = "https://api.acleddata.com/acled/read"

# Oil-relevant event types (we skip protests/riots — low supply impact)
OIL_EVENT_TYPES = [
    "Battles",
    "Explosions/Remote violence",
    "Violence against civilians",
    "Strategic developments",
]

# Oil-producing regions: country + admin1 regions near infrastructure
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


async def scrape_acled(days: int = 3) -> list[dict]:
    """
    Fetch recent conflict events from ACLED in oil-producing countries.
    Returns structured events filtered for supply-relevant incidents.
    """
    api_key = settings.ACLED_API_KEY
    email = settings.ACLED_EMAIL
    if not api_key or not email:
        print("[ACLED] No ACLED_API_KEY or ACLED_EMAIL configured — skipping.")
        return []

    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    all_events = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        for country in OIL_COUNTRIES:
            try:
                events = await _fetch_country(client, api_key, email, country, cutoff)
                all_events.extend(events)
            except Exception as e:
                print(f"[ACLED] Error fetching {country}: {e}")

    print(f"[ACLED] Found {len(all_events)} conflict events in oil regions.")
    return all_events


async def _fetch_country(
    client: httpx.AsyncClient,
    api_key: str,
    email: str,
    country: str,
    cutoff_date: str,
) -> list[dict]:
    """Fetch ACLED events for a single country since cutoff_date."""
    params = {
        "key": api_key,
        "email": email,
        "country": country,
        "event_date": cutoff_date,
        "event_date_where": ">=",
        "limit": 50,
    }

    response = await client.get(ACLED_API_URL, params=params)
    response.raise_for_status()
    data = response.json()

    if not data.get("success") or not data.get("data"):
        return []

    events = []
    for row in data["data"]:
        event_type = row.get("event_type", "")
        if event_type not in OIL_EVENT_TYPES:
            continue

        notes = row.get("notes", "")
        fatalities = int(row.get("fatalities", 0) or 0)
        sub_type = row.get("sub_event_type", "")
        location = row.get("location", "")
        admin1 = row.get("admin1", "")
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

        events.append({
            "headline": headline,
            "source": "ACLED Conflict Data",
            "source_url": None,
            "raw_content": raw_content,
            "event_time": event_time,
        })

    return events
