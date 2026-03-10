# Oil Intelligence Index — Project Status

> **Last Updated:** 2026-03-10 23:42 (UTC+8)  
> **Current Phase:** Phase 6 — Build Dashboard UI (Complete)

---

## Tech Stack (Confirmed)

| Layer | Technology | Deployment |
|---|---|---|
| UI | Next.js + Tailwind CSS | Vercel (Hobby / Free) |
| API | Python (FastAPI) | Render (Free) |
| Database | Neon DB (Postgres) | Neon (Free tier) |
| LLM | OpenAI (gpt-4o-mini) | API Key |

---

## Phase Tracker

### ✅ Phase 1: Research & Source Identification
- Identified OSINT data sources (ACLED, NASA FIRMS, AIS, Telegram).
- Found reference GitHub repos (World Monitor, Global Threat Map, Crisis Map).

### ✅ Phase 2: Architecture & Tool Selection
- Defined the "Buy/Sell" indicator concept (0-100 index like Fear/Greed).
- Confirmed full tech stack above.

### ✅ Phase 3: Documentation
- Created `docs/PRD.md`, `docs/implementation_plan.md`, `docs/research_sources.md`.
- Created `claude.md` at repo root for AI agent context.

### 🔄 Phase 4: Project Scaffolding (CURRENT)
- [x] Created `ui/` — Next.js + Tailwind initialized.
- [x] Created `api/` — FastAPI skeleton with:
  - `app/models/` — SQLAlchemy models (Event, IndexSnapshot).
  - `app/routers/` — API endpoints (index, events).
  - `app/services/` — AI scorer (OpenAI), index calculator.
  - `app/scrapers/` — RSS feed scraper.
- [x] Created `shared/` — TypeScript types and constants.
- [x] Created `.gitignore` and `.env.example`.
- [x] Created `status.md` (this file).

### ⬜ Phase 5: Wire Up Backend (NEXT)
- [ ] Set up Neon DB and run initial migration.
- [ ] Connect routers to real DB queries.
- [ ] Build the scrape → score → store pipeline.
- [ ] Add APScheduler cron job for automated scraping.

### ⬜ Phase 6: Build Dashboard UI
- [ ] Create the main gauge/indicator component.
- [ ] Create the intelligence feed component.
- [ ] Connect UI to API endpoints.

### ⬜ Phase 7: Deploy
- [ ] Deploy UI to Vercel.
- [ ] Deploy API to Render.
- [ ] Configure Neon DB production connection.

---

## Directory Structure

```
baby-oil/
├── claude.md              # AI agent context file
├── status.md              # This file — project status tracker
├── .gitignore
│
├── docs/                  # Project documentation
│   ├── PRD.md
│   ├── implementation_plan.md
│   └── research_sources.md
│
├── api/                   # Python FastAPI backend
│   ├── main.py            # Entry point
│   ├── requirements.txt
│   ├── .env.example
│   └── app/
│       ├── config.py
│       ├── models/
│       │   ├── database.py
│       │   └── schemas.py
│       ├── routers/
│       │   ├── index.py
│       │   └── events.py
│       ├── services/
│       │   ├── scorer.py
│       │   └── calculator.py
│       └── scrapers/
│           └── rss_scraper.py
│
├── ui/                    # Next.js + Tailwind frontend
│   ├── package.json
│   ├── src/app/
│   └── ...
│
└── shared/                # Shared types and constants
    ├── package.json
    └── types.ts
```
