import asyncio
from app.scrapers.firms_scraper import scrape_firms
from app.config import settings

async def main():
    print(f"Key configured: {'Yes' if settings.NASA_FIRMS_MAP_KEY else 'No'}")
    print("Testing FIRMS scraper...")
    events = await scrape_firms(days=1)
    print(f"Found {len(events)} events.")
    for e in events[:3]:
        print("-", e["headline"])

if __name__ == "__main__":
    asyncio.run(main())
