"""
NASA FIRMS Scraper
==================
Fetches near-real-time thermal anomaly (fire/hotspot) data from NASA's
Fire Information for Resource Management System (FIRMS).

This detects refinery fires, gas flaring anomalies, and pipeline
infrastructure damage near major oil-producing regions — often before
it reaches mainstream news.

Requires a free MAP_KEY from: https://firms.modaps.eosdis.nasa.gov/api/area/
"""

import httpx
from datetime import datetime

from app.config import settings


# Key oil infrastructure regions (bounding boxes: W,S,E,N)
OIL_REGIONS = [
    {
        "name": "Persian Gulf / Strait of Hormuz",
        "bbox": "44,22,60,32",  # Iraq, Kuwait, Iran, Saudi coast, UAE
    },
    {
        "name": "Libya / North Africa",
        "bbox": "9,25,25,34",
    },
    {
        "name": "Nigeria / Niger Delta",
        "bbox": "2,4,9,8",
    },
    {
        "name": "Gulf of Mexico",
        "bbox": "-98,18,-82,31",
    },
    {
        "name": "Western Russia / Caspian",
        "bbox": "38,42,56,62",
    },
]

FIRMS_API_URL = "https://firms.modaps.eosdis.nasa.gov/api/area/csv"


async def scrape_firms(days: int = 1) -> list[dict]:
    """
    Fetch thermal anomalies from NASA FIRMS for oil-critical regions.
    Returns structured events for high-confidence hotspots only.
    """
    map_key = settings.NASA_FIRMS_MAP_KEY
    if not map_key:
        print("[FIRMS] No NASA_FIRMS_MAP_KEY configured — skipping.")
        return []

    all_events = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        for region in OIL_REGIONS:
            try:
                events = await _fetch_region(client, map_key, region, days)
                all_events.extend(events)
            except Exception as e:
                print(f"[FIRMS] Error fetching {region['name']}: {e}")

    print(f"[FIRMS] Found {len(all_events)} significant thermal anomalies.")
    return all_events


async def _fetch_region(
    client: httpx.AsyncClient,
    map_key: str,
    region: dict,
    days: int,
) -> list[dict]:
    """Fetch FIRMS data for a single region and filter for significant events."""
    # Use VIIRS sensor (higher resolution than MODIS)
    url = f"{FIRMS_API_URL}/{map_key}/VIIRS_SNPP_NRT/{region['bbox']}/{days}"

    response = await client.get(url)
    response.raise_for_status()

    lines = response.text.strip().split("\n")
    if len(lines) <= 1:
        return []

    header = lines[0].split(",")
    events = []

    for line in lines[1:]:
        cols = line.split(",")
        if len(cols) < len(header):
            continue

        row = dict(zip(header, cols))

        # Filter: only high-confidence detections (≥ "nominal" or "high")
        confidence = row.get("confidence", "low")
        if confidence == "low":
            continue

        # Filter: only bright fires (FRP > 10 MW = significant)
        frp = float(row.get("frp", 0))
        if frp < 10:
            continue

        lat = row.get("latitude", "?")
        lon = row.get("longitude", "?")
        acq_date = row.get("acq_date", "")
        acq_time = row.get("acq_time", "")

        event_time = None
        try:
            event_time = datetime.strptime(
                f"{acq_date} {acq_time}", "%Y-%m-%d %H%M"
            )
        except ValueError:
            pass

        events.append({
            "headline": f"Thermal anomaly detected in {region['name']} — {frp:.0f} MW at ({lat}, {lon})",
            "source": "NASA FIRMS (Satellite)",
            "source_url": f"https://firms.modaps.eosdis.nasa.gov/map/#d:24hrs;l:fires;@{lon},{lat},10z",
            "raw_content": (
                f"Region: {region['name']}. "
                f"Fire Radiative Power: {frp} MW. "
                f"Confidence: {confidence}. "
                f"Coordinates: {lat}, {lon}. "
                f"Date: {acq_date} {acq_time}."
            ),
            "event_time": event_time,
        })

    return events
