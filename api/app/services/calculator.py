"""
Index Calculator
================
Computes the Oil Intelligence Index (0-100) from recent scored events.
Uses a time-weighted average favoring recent, high-relevance events.
"""

from datetime import datetime, timedelta, timezone


def calculate_index(events: list[dict]) -> dict:
    """
    Calculate the Oil Intelligence Index from a list of scored events.

    Each event dict should have:
      - relevance_score: int (1-10)
      - signal_direction: float (-1.0 to +1.0)
      - created_at: datetime

    Returns:
      {"score": int 0-100, "label": str}
    """
    if not events:
        return {"score": 50, "label": "Neutral"}

    now = datetime.now(timezone.utc)
    total_weight = 0.0
    weighted_signal = 0.0

    for event in events:
        relevance = event.get("relevance_score", 1)
        direction = event.get("signal_direction", 0.0)
        created = event.get("created_at", now)

        # Time decay: events lose half their weight every 6 hours
        if isinstance(created, str):
            created = datetime.fromisoformat(created)
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        
        hours_old = max(0, (now - created).total_seconds() / 3600)
        time_weight = 0.5 ** (hours_old / 6.0)

        # Final weight = relevance * time_decay
        weight = relevance * time_weight
        total_weight += weight
        weighted_signal += direction * weight

    if total_weight == 0:
        return {"score": 50, "label": "Neutral"}

    # Normalize: weighted_signal / total_weight gives a value in [-1, 1]
    normalized = weighted_signal / total_weight

    # Map [-1, 1] to [0, 100]
    score = int(round((normalized + 1) * 50))
    score = max(0, min(100, score))

    label = _score_to_label(score)
    return {"score": score, "label": label}


def _score_to_label(score: int) -> str:
    if score <= 30:
        return "Strong Sell"
    elif score <= 45:
        return "Sell"
    elif score <= 55:
        return "Neutral"
    elif score <= 70:
        return "Buy"
    else:
        return "Strong Buy"
