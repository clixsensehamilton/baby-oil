"""
/api/v1/index — serves the current Oil Intelligence Index value.
"""

from datetime import timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.database import get_db
from app.models.schemas import Event, IndexSnapshot
from app.services.calculator import calculate_index

router = APIRouter()


def _utc_iso(dt) -> str | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


@router.get("/index")
async def get_current_index(db: Session = Depends(get_db)):
    """
    Computes and returns the current Oil Intelligence Index (0-100)
    from the most recent scored events in the database.
    """
    recent_events = (
        db.query(Event)
        .order_by(desc(Event.created_at))
        .limit(100)
        .all()
    )

    events_data = [
        {
            "relevance_score": e.relevance_score,
            "signal_direction": e.signal_direction,
            "created_at": e.created_at,
        }
        for e in recent_events
    ]

    result = calculate_index(events_data)

    return {
        "score": result["score"],
        "label": result["label"],
        "event_count": len(recent_events),
        "updated_at": _utc_iso(recent_events[0].created_at) if recent_events else None,
    }


@router.get("/index/history")
async def get_index_history(
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """
    Returns historical index snapshots for charting.
    """
    snapshots = (
        db.query(IndexSnapshot)
        .order_by(desc(IndexSnapshot.created_at))
        .limit(limit)
        .all()
    )

    return {
        "history": [
            {
                "score": s.score,
                "label": s.label,
                "event_count": s.event_count,
                "created_at": s.created_at.isoformat(),
            }
            for s in snapshots
        ]
    }
