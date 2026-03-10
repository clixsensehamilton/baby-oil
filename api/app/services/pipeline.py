"""
Pipeline Orchestrator
=====================
Coordinates the full cycle: Scrape → Score → Store → Snapshot.
This is the core engine that runs on a schedule.
"""

from sqlalchemy.orm import Session

from app.models.database import SessionLocal
from app.models.schemas import Event, IndexSnapshot
from app.scrapers.rss_scraper import scrape_rss_feeds
from app.scrapers.firms_scraper import scrape_firms
from app.scrapers.acled_scraper import scrape_acled
from app.scrapers.eia_scraper import scrape_eia
from app.services.scorer import score_event
from app.services.calculator import calculate_index


async def run_pipeline():
    """
    Full pipeline execution:
    1. Scrape raw events from all configured sources.
    2. Score each event using OpenAI.
    3. Store scored events in the database.
    4. Recompute the index and save a snapshot.
    """
    print("[Pipeline] Starting scrape cycle...")

    # Step 1: Scrape from all sources (primary OSINT first, news supplementary)
    acled_events = await scrape_acled()
    eia_events = await scrape_eia()
    firms_events = await scrape_firms()
    rss_events = await scrape_rss_feeds()
    raw_events = acled_events + eia_events + firms_events + rss_events
    print(
        f"[Pipeline] Scraped: "
        f"{len(acled_events)} ACLED + "
        f"{len(eia_events)} EIA + "
        f"{len(firms_events)} FIRMS + "
        f"{len(rss_events)} RSS = "
        f"{len(raw_events)} total."
    )

    if not raw_events:
        print("[Pipeline] No events found. Skipping.")
        return

    db = SessionLocal()
    new_events = []

    try:
        # Step 2 & 3: Score and Store
        for raw in raw_events:
            # Check for duplicates by headline
            existing = (
                db.query(Event)
                .filter(Event.headline == raw["headline"])
                .first()
            )
            if existing:
                continue

            # Score with AI
            scores = await score_event(
                headline=raw["headline"],
                raw_content=raw.get("raw_content", ""),
            )

            # Create and store event
            event = Event(
                headline=raw["headline"],
                source=raw["source"],
                source_url=raw.get("source_url"),
                raw_content=raw.get("raw_content"),
                event_time=raw.get("event_time"),
                relevance_score=scores["relevance_score"],
                signal_direction=scores["signal_direction"],
                signal_label=scores["signal_label"],
                ai_reasoning=scores["reasoning"],
            )
            db.add(event)
            new_events.append(event)

        db.commit()
        print(f"[Pipeline] Stored {len(new_events)} new scored events.")

        # Step 4: Recompute index and save snapshot
        recent = db.query(Event).order_by(Event.created_at.desc()).limit(100).all()
        events_data = [
            {
                "relevance_score": e.relevance_score,
                "signal_direction": e.signal_direction,
                "created_at": e.created_at,
            }
            for e in recent
        ]
        result = calculate_index(events_data)

        snapshot = IndexSnapshot(
            score=result["score"],
            label=result["label"],
            event_count=len(recent),
        )
        db.add(snapshot)
        db.commit()

        print(f"[Pipeline] Index updated: {result['score']} ({result['label']})")

    except Exception as e:
        db.rollback()
        print(f"[Pipeline] Error: {e}")
        raise
    finally:
        db.close()
