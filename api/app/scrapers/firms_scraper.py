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


# Cluster resolution in degrees (~50 km grid)
CLUSTER_GRID_DEG = 0.5
# Max clusters to emit per region (highest FRP wins)
MAX_CLUSTERS_PER_REGION = 3
# Minimum FRP threshold (MW) — raise to skip minor flaring
MIN_FRP_MW = 50


async def _fetch_region(
    client: httpx.AsyncClient,
    map_key: str,
    region: dict,
    days: int,
) -> list[dict]:
    """
    Fetch FIRMS data for a single region, cluster nearby hotspots into
    single events, and return the top MAX_CLUSTERS_PER_REGION by total FRP.
    """
    url = f"{FIRMS_API_URL}/{map_key}/VIIRS_SNPP_NRT/{region['bbox']}/{days}"

    response = await client.get(url)
    response.raise_for_status()

    lines = response.text.strip().split("\n")
    if len(lines) <= 1:
        return []

    header = lines[0].split(",")

    # clusters: grid_key -> {total_frp, count, peak_frp, lat, lon, event_time, acq_date}
    clusters: dict[str, dict] = {}

    for line in lines[1:]:
        cols = line.split(",")
        if len(cols) < len(header):
            continue

        row = dict(zip(header, cols))

        confidence = row.get("confidence", "low")
        if confidence == "low":
            continue

        try:
            frp = float(row.get("frp", 0))
            lat = float(row.get("latitude", 0))
            lon = float(row.get("longitude", 0))
        except ValueError:
            continue

        if frp < MIN_FRP_MW:
            continue

        # Snap to grid cell
        grid_lat = round(round(lat / CLUSTER_GRID_DEG) * CLUSTER_GRID_DEG, 1)
        grid_lon = round(round(lon / CLUSTER_GRID_DEG) * CLUSTER_GRID_DEG, 1)
        grid_key = f"{grid_lat},{grid_lon}"

        acq_date = row.get("acq_date", "")
        acq_time = row.get("acq_time", "")
        event_time = None
        try:
            event_time = datetime.strptime(f"{acq_date} {acq_time}", "%Y-%m-%d %H%M")
        except ValueError:
            pass

        if grid_key not in clusters:
            clusters[grid_key] = {
                "total_frp": 0.0,
                "peak_frp": 0.0,
                "count": 0,
                "lat": grid_lat,
                "lon": grid_lon,
                "event_time": event_time,
                "acq_date": acq_date,
            }

        c = clusters[grid_key]
        c["total_frp"] += frp
        c["count"] += 1
        if frp > c["peak_frp"]:
            c["peak_frp"] = frp
            c["event_time"] = event_time

    if not clusters:
        return []

    # Sort by total FRP descending, take top N
    top = sorted(clusters.values(), key=lambda c: c["total_frp"], reverse=True)[:MAX_CLUSTERS_PER_REGION]

    events = []
    for c in top:
        lat, lon = c["lat"], c["lon"]
        date_str = c["acq_date"]
        events.append({
            "headline": (
                f"Thermal cluster in {region['name']} ({lat}°, {lon}°) — "
                f"{date_str}, {c['total_frp']:.0f} MW total ({c['count']} detections)"
            ),
            "source": "NASA FIRMS (Satellite)",
            "source_url": f"https://firms.modaps.eosdis.nasa.gov/map/#d:24hrs;l:fires;@{lon},{lat},10z",
            "raw_content": (
                f"Region: {region['name']}. "
                f"Cluster center: {lat}°N, {lon}°E. "
                f"Total Fire Radiative Power: {c['total_frp']:.0f} MW across {c['count']} detections. "
                f"Peak FRP: {c['peak_frp']:.0f} MW. "
                f"Date: {date_str}."
            ),
            "event_time": c["event_time"],
        })

    return events
