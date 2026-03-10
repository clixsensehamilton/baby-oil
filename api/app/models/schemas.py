"""
SQLAlchemy ORM models for the Oil Intelligence Index.
"""

import uuid
from datetime import datetime

from sqlalchemy import String, Integer, Float, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base


class Event(Base):
    """A single processed OSINT intelligence event."""

    __tablename__ = "events"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    headline: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_content: Mapped[str | None] = mapped_column(Text, nullable=True)

    # AI-assigned scores
    relevance_score: Mapped[int] = mapped_column(
        Integer, default=0, comment="1-10 relevance to oil supply"
    )
    signal_direction: Mapped[float] = mapped_column(
        Float, default=0.0, comment="-1.0 (bearish) to +1.0 (bullish)"
    )
    signal_label: Mapped[str] = mapped_column(
        String(20), default="neutral", comment="bullish | bearish | neutral"
    )
    ai_reasoning: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="LLM explanation for the score"
    )

    # Timestamps
    event_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )


class IndexSnapshot(Base):
    """A point-in-time snapshot of the computed Oil Intelligence Index."""

    __tablename__ = "index_snapshots"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    score: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="0-100 index value"
    )
    label: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="Strong Sell / Sell / Neutral / Buy / Strong Buy"
    )
    event_count: Mapped[int] = mapped_column(
        Integer, default=0, comment="Number of events factored into this snapshot"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
