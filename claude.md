# Oil Intelligence Index - Context for Claude Code

This file is designed to give you (Claude) immediate context about the current project when this repository is opened in a new session.

## Project Overview
We are building the **Oil Intelligence Index**, a dashboard application that acts as a real-time "Buy/Sell" indicator for global oil markets based entirely on Open-Source Intelligence (OSINT).

Instead of relying on delayed mainstream news, this application ingests raw data (geopolitical conflict events from ACLED, vessel tracking from AIS, infrastructure anomalies from NASA FIRMS, and raw Telegram combat/political feeds), passes it through an AI engine to determine the severity and direction of the supply impact, and updates a live index indicator.

## What it is NOT
We are **not** building a 3D visual globe or an interactive map. We are strictly building a quantitative index and feed specifically laser-focused on oil supply disruption and geopolitics affecting energy.

## Tech Stack
| Layer | Technology | Deployment |
|---|---|---|
| UI | Next.js + Tailwind CSS | Vercel (Hobby / Free) |
| API | Python (FastAPI) | Render (Free) |
| Database | Neon DB (Postgres) | Neon (Free tier) |
| LLM | OpenAI API (gpt-4o-mini) | API Key |

## Architecture
1.  **Ingestion Hub (`api/app/scrapers/`):** Scrapes RSS feeds, Telegram, and APIs for raw intelligence.
2.  **Analysis Engine (`api/app/services/`):**
    -   `scorer.py`: Calls OpenAI to assign Relevance (1-10) and Signal Direction (-1 to +1).
    -   `calculator.py`: Computes the 0-100 index using a time-weighted average of scored events.
3.  **API Layer (`api/app/routers/`):** Serves the index score and event feed to the frontend.
4.  **Frontend Dashboard (`ui/`):** Next.js + Tailwind app displaying a gauge indicator and scrolling intelligence feed.

## Key Files
- **Status tracker:** `status.md` (check this first for current project state)
- **PRD:** `docs/PRD.md`
- **Implementation Plan:** `docs/implementation_plan.md`
- **Data Sources Research:** `docs/research_sources.md`
- **Shared Types:** `shared/types.ts`
- **API Entry Point:** `api/main.py`
- **API Config Template:** `api/.env.example`

## How to Run Locally
```bash
# UI (Next.js)
cd ui && npm run dev

# API (FastAPI)
cd api && pip install -r requirements.txt && uvicorn main:app --reload
```
