"""
RSS Feed Scraper
================
Scrapes OSINT-relevant RSS feeds for oil/energy/conflict news.
This is the first and simplest scraper to get the pipeline working.
"""

import feedparser
import httpx
from datetime import datetime


# Curated list of high-signal RSS feeds
DEFAULT_FEEDS = [
    {
        "name": "Reuters Energy",
        "url": "https://reutersagency.com/feed/?best-topics=energy&post_type=best",
    },
    {
        "name": "OilPrice.com",
        "url": "https://oilprice.com/rss/main",
    },
    {
        "name": "CNBC Energy",
        "url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000856",
    },
]


async def scrape_rss_feeds(feeds: list[dict] | None = None) -> list[dict]:
    """
    Scrape configured RSS feeds and return raw event dicts.
    Each dict has: headline, source, source_url, raw_content, event_time.
    """
    feeds = feeds or DEFAULT_FEEDS
    all_events = []

    for feed_config in feeds:
        try:
            events = await _parse_feed(feed_config)
            all_events.extend(events)
        except Exception as e:
            print(f"[Scraper] Error scraping {feed_config['name']}: {e}")

    return all_events


async def _parse_feed(feed_config: dict) -> list[dict]:
    """Parse a single RSS feed and return structured events."""
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        response = await client.get(feed_config["url"])
        response.raise_for_status()

    parsed = feedparser.parse(response.text)
    events = []

    for entry in parsed.entries[:10]:  # Limit to 10 most recent per feed
        event_time = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            event_time = datetime(*entry.published_parsed[:6])

        events.append({
            "headline": entry.get("title", "No title"),
            "source": feed_config["name"],
            "source_url": entry.get("link", ""),
            "raw_content": entry.get("summary", ""),
            "event_time": event_time,
        })

    return events
