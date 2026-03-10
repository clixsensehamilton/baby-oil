"""
Oil Intelligence Index — API Entry Point
=========================================
FastAPI application serving the processed intelligence feed
and the computed Buy/Sell index to the frontend dashboard.
"""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.routers import index, events
from app.config import settings
from app.models.database import Base, engine
from app.services.pipeline import run_pipeline


# --- Lifecycle ---

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic."""
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    print("[Startup] Database tables ensured.")

    # Schedule the scrape pipeline
    scheduler.add_job(
        lambda: asyncio.ensure_future(run_pipeline()),
        "interval",
        minutes=settings.SCRAPE_INTERVAL_MINUTES,
        id="scrape_pipeline",
        replace_existing=True,
    )
    scheduler.start()
    print(f"[Startup] Scheduler started — pipeline runs every {settings.SCRAPE_INTERVAL_MINUTES} min.")

    yield

    # Shutdown
    scheduler.shutdown()
    print("[Shutdown] Scheduler stopped.")


# --- App ---

app = FastAPI(
    title="Oil Intelligence Index API",
    description="OSINT-powered Buy/Sell indicator for global oil markets.",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow the Next.js frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": app.version}


@app.post("/api/v1/pipeline/trigger")
async def trigger_pipeline():
    """Manually trigger a scrape cycle (for testing)."""
    await run_pipeline()
    return {"status": "pipeline_complete"}


# Register route modules
app.include_router(index.router, prefix="/api/v1", tags=["Index"])
app.include_router(events.router, prefix="/api/v1", tags=["Events"])
