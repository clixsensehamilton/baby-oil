"""
Database initialization utility.
Run this script to create all tables in Neon DB.
Usage: python -m app.models.init_db
"""

from app.models.database import Base, engine
from app.models.schemas import Event, IndexSnapshot  # noqa: F401 — import to register models


def init_db():
    """Create all tables defined by SQLAlchemy models."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Done! Tables created successfully.")


if __name__ == "__main__":
    init_db()
