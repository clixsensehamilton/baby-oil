"""
EIA Petroleum Data Scraper
===========================
Fetches objective, hard-number petroleum data from the US Energy
Information Administration (EIA) API v2.

Key data: weekly crude oil inventory changes — the single most
market-moving data point in oil markets. Released every Wednesday
at 10:30 AM ET.

Unlike news, this is raw government data that cannot be spun or
manipulated. An unexpected inventory draw = bullish; build = bearish.

Requires a free API key from: https://www.eia.gov/opendata/register.php
"""

import httpx
from datetime import datetime

from app.config import settings

EIA_API_BASE = "https://api.eia.gov/v2"

# Data series we track — each produces one event per scrape
DATA_SERIES = [
    {
        "name": "US Crude Oil Stocks (excl. SPR)",
        "route": "/petroleum/stoc/wstk/data/",
        "facets": {
            "product": "EPC0",
            "process": "SAE",
            "duoarea": "NUS",
        },
        "unit": "thousand barrels",
        "draw_is_bullish": True,
    },
    {
        "name": "US Crude Oil Production",
        "route": "/petroleum/sum/sndw/data/",
        "facets": {
            "product": "EPC0",
            "process": "FP1",
            "duoarea": "NUS",
        },
        "unit": "thousand barrels/day",
        "draw_is_bullish": False,  # production drop = supply tightening = bullish
    },
]


async def scrape_eia() -> list[dict]:
    """
    Fetch the latest EIA petroleum data and compute week-over-week changes.
    Returns events with pre-computed signal direction (no AI scoring needed
    for the direction — the numbers speak for themselves).
    """
    api_key = settings.EIA_API_KEY
    if not api_key:
        print("[EIA] No EIA_API_KEY configured — skipping.")
        return []

    all_events = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        for series in DATA_SERIES:
            try:
                event = await _fetch_series(client, api_key, series)
                if event:
                    all_events.append(event)
            except Exception as e:
                print(f"[EIA] Error fetching {series['name']}: {e}")

    print(f"[EIA] Generated {len(all_events)} data events.")
    return all_events


async def _fetch_series(
    client: httpx.AsyncClient,
    api_key: str,
    series: dict,
) -> dict | None:
    """
    Fetch the 2 most recent data points for a series, compute
    the week-over-week change, and return a structured event.
    """
    url = f"{EIA_API_BASE}{series['route']}"

    params = {
        "api_key": api_key,
        "frequency": "weekly",
        "data[0]": "value",
        "sort[0][column]": "period",
        "sort[0][direction]": "desc",
        "length": "2",
    }

    # Add facet filters
    for facet_key, facet_val in series["facets"].items():
        params[f"facets[{facet_key}][]"] = facet_val

    response = await client.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    rows = data.get("response", {}).get("data", [])
    if len(rows) < 2:
        return None

    latest = rows[0]
    previous = rows[1]

    latest_val = float(latest.get("value", 0))
    prev_val = float(previous.get("value", 0))
    change = latest_val - prev_val
    period = latest.get("period", "")

    if prev_val == 0:
        return None

    change_pct = (change / prev_val) * 100

    # Determine direction from raw data — no AI needed for this
    if series["draw_is_bullish"]:
        # For stocks: draw (negative change) = bullish
        direction_text = "DRAW" if change < 0 else "BUILD"
    else:
        # For production: drop (negative change) = bullish
        direction_text = "DECLINE" if change < 0 else "INCREASE"

    headline = (
        f"EIA: {series['name']} {direction_text} — "
        f"{abs(change):,.0f} {series['unit']} ({change_pct:+.1f}%) "
        f"week ending {period}"
    )

    raw_content = (
        f"Data source: US Energy Information Administration (government data). "
        f"Series: {series['name']}. "
        f"Latest value: {latest_val:,.0f} {series['unit']} (week ending {period}). "
        f"Previous value: {prev_val:,.0f} {series['unit']} (week ending {previous.get('period', '')}). "
        f"Change: {change:+,.0f} {series['unit']} ({change_pct:+.1f}%). "
        f"Direction: {direction_text}. "
        f"NOTE: This is official US government data, not news or opinion."
    )

    event_time = None
    try:
        event_time = datetime.strptime(period, "%Y-%m-%d")
    except ValueError:
        pass

    return {
        "headline": headline,
        "source": "EIA (US Gov Data)",
        "source_url": "https://www.eia.gov/petroleum/supply/weekly/",
        "raw_content": raw_content,
        "event_time": event_time,
    }
