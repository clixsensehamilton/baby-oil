"""
/api/v1/events — serves the processed intelligence event feed.
"""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.database import get_db
from app.models.schemas import Event

router = APIRouter()


def _utc_iso(dt: datetime | None) -> str | None:
    """Ensure datetime is serialized with UTC timezone suffix."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


@router.get("/events")
async def get_events(
    limit: int = Query(default=30, le=100),
    offset: int = Query(default=0, ge=0),
    min_relevance: int = Query(default=1, ge=1, le=10),
    sort: str = Query(default="recent", regex="^(recent|relevance)$"),
    days: int = Query(default=7, ge=1, le=30),
    db: Session = Depends(get_db),
):
    """
    Returns a paginated list of processed OSINT events.
    Supports sorting by recency or relevance, filtering by min relevance,
    and limiting to a time window (days).
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    query = (
        db.query(Event)
        .filter(Event.relevance_score >= min_relevance)
        .filter(Event.created_at >= cutoff)
    )

    # Sort order
    if sort == "relevance":
        query = query.order_by(desc(Event.relevance_score), desc(Event.created_at))
    else:
        query = query.order_by(desc(Event.created_at))

    total = query.count()
    events = query.offset(offset).limit(limit).all()

    return {
        "events": [
            {
                "id": e.id,
                "headline": e.headline,
                "source": e.source,
                "source_url": e.source_url,
                "relevance_score": e.relevance_score,
                "signal_direction": e.signal_direction,
                "signal_label": e.signal_label,
                "ai_reasoning": e.ai_reasoning,
                "event_time": _utc_iso(e.event_time),
                "created_at": _utc_iso(e.created_at),
            }
            for e in events
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/events/{event_id}")
async def get_event_detail(event_id: str, db: Session = Depends(get_db)):
    """
    Returns full details for a specific event.
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return {"error": "Event not found"}

    return {
        "id": event.id,
        "headline": event.headline,
        "source": event.source,
        "source_url": event.source_url,
        "raw_content": event.raw_content,
        "relevance_score": event.relevance_score,
        "signal_direction": event.signal_direction,
        "signal_label": event.signal_label,
        "ai_reasoning": event.ai_reasoning,
        "event_time": _utc_iso(event.event_time),
        "created_at": _utc_iso(event.created_at),
    }
